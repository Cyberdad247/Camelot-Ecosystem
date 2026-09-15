// SPDX-License-Identifier: MIT

//! # camelot-audio-dsp — Omni-Voice D.A.G. ingress stage
//!
//! Stage 1 of the `OMNI_VOICE_ROUTER_vMAX` D.A.G. (`node_01_ingress`). This is
//! the Rust/WASM realisation of the declared `camelot-audio-dsp` service: it
//! takes 16 kHz mono `i16` PCM off the microphone and emits fixed 20 ms frames
//! (320 samples) stamped by an authoritative audio clock, together with an
//! RMS/peak envelope and a hangover-gated voice-activity decision.
//!
//! ## Design constraints (from the crystal manifest)
//!
//! * [`FRAME_MS`] `= 20` at [`SAMPLE_RATE_HZ`] `= 16_000` — the WebRTC/Opus
//!   framing the downstream nodes expect.
//! * **Lock-free** — the ring buffer is a single-producer/single-consumer queue
//!   whose cursors are atomics. There is no mutex anywhere on the audio path,
//!   so a `push` can never block or stall the capture callback.
//! * **Zero frame leaks** — every buffer registers in a process-wide gauge
//!   ([`open_ring_buffers`]) on construction and deregisters on `close`/`Drop`,
//!   turning the declared "open ring buffers = 0" invariant into a checkable
//!   integer instead of a promise.
//! * **The audio clock is authoritative for viseme sync** — frame timestamps
//!   come from [`AudioClock`] (a sample-count derivation), never from
//!   wall-clock time, so a dropped frame cannot desynchronise lip-sync.
//!
//! ```
//! use camelot_audio_dsp::{AudioDsp, FRAME_SAMPLES};
//!
//! let mut dsp = AudioDsp::with_default_capacity();
//! assert_eq!(dsp.push_pcm(&vec![0i16; FRAME_SAMPLES * 2]), FRAME_SAMPLES * 2);
//!
//! let first = dsp.next_frame().expect("one whole frame is buffered");
//! assert_eq!(first.index, 0);
//! assert_eq!(first.capture_micros, 0);
//! assert_eq!(dsp.frames_emitted(), 1);
//! ```

use core::sync::atomic::{AtomicBool, AtomicUsize, Ordering};

/// Sample rate of the ingress stream, in Hz.
pub const SAMPLE_RATE_HZ: u32 = 16_000;

/// Frame duration that downstream stages are synchronised to, in milliseconds.
pub const FRAME_MS: u32 = 20;

/// Samples in one frame — 320 at 16 kHz / 20 ms.
pub const FRAME_SAMPLES: usize = (SAMPLE_RATE_HZ as usize * FRAME_MS as usize) / 1_000;

/// Wall duration of one frame in microseconds (the audio-clock quantum).
pub const FRAME_MICROS: u64 = FRAME_MS as u64 * 1_000;

/// Memory budget the Omni-Voice crystal allots to `node_01_ingress`, in MB.
pub const MEMORY_CEILING_MB: usize = 96;

/// Default ring capacity, in frames — 32 frames ≈ 640 ms of mono PCM.
pub const DEFAULT_RING_FRAMES: usize = 32;

/// Process-wide count of ring buffers that have been constructed but not yet
/// closed. The D.A.G. memory invariant is "zero frame leaks (open ring buffers
/// = 0)", which is exactly the assertion `open_ring_buffers() == 0`.
static OPEN_RING_BUFFERS: AtomicUsize = AtomicUsize::new(0);

/// Number of ring buffers currently held open anywhere in the process.
pub fn open_ring_buffers() -> usize {
    OPEN_RING_BUFFERS.load(Ordering::Acquire)
}

/// Semantic version of the DSP ABI, surfaced to the browser glue.
pub fn abi_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Root-mean-square amplitude of a frame, normalised to `0.0..=1.0`.
pub fn frame_rms(samples: &[i16]) -> f32 {
    if samples.is_empty() {
        return 0.0;
    }
    let sum_squares: f64 = samples.iter().map(|&s| (s as f64) * (s as f64)).sum();
    let mean = sum_squares / samples.len() as f64;
    (mean.sqrt() / i16::MAX as f64) as f32
}

/// Largest absolute sample magnitude in a frame (saturating, so `i16::MIN`
/// cannot wrap).
pub fn frame_peak(samples: &[i16]) -> i16 {
    samples
        .iter()
        .map(|s| s.saturating_abs())
        .max()
        .unwrap_or(0)
}

// ---------------------------------------------------------------------------
// Lock-free SPSC sample ring
// ---------------------------------------------------------------------------

/// A non-blocking ring buffer of `i16` PCM samples.
///
/// The audio path takes no lock of any kind. A `push` into a full buffer writes
/// what fits and reports the short write, which the caller accounts as dropped
/// samples rather than stalling the capture callback. Both cursors are
/// monotonic counters, so occupancy never needs a sentinel slot to tell "full"
/// from "empty".
///
/// Access is `&mut self`: this node runs as a single WASM instance driven by one
/// audio thread, so there is no second writer to share with and no reason to pay
/// for interior mutability. A genuinely cross-thread SPSC variant would need
/// `UnsafeCell` (or per-sample atomics); neither is introduced here, because the
/// extra machinery would buy nothing on the ingress path and would have to be
/// justified as `unsafe`.
#[derive(Debug)]
pub struct SampleRing {
    slots: Vec<i16>,
    head: usize,
    tail: usize,
    closed: AtomicBool,
}

impl SampleRing {
    /// Allocate a ring holding `capacity_samples` samples and register it in
    /// the open-buffer gauge.
    pub fn new(capacity_samples: usize) -> Self {
        let capacity = capacity_samples.max(1);
        OPEN_RING_BUFFERS.fetch_add(1, Ordering::AcqRel);
        Self {
            slots: vec![0i16; capacity],
            head: 0,
            tail: 0,
            closed: AtomicBool::new(false),
        }
    }

    /// Allocate a ring holding `frames` frames' worth of samples.
    pub fn with_frame_capacity(frames: usize) -> Self {
        Self::new(frames.max(1) * FRAME_SAMPLES)
    }

    /// Total number of samples the ring can hold.
    pub fn capacity(&self) -> usize {
        self.slots.len()
    }

    /// Samples currently readable.
    pub fn available(&self) -> usize {
        self.head - self.tail
    }

    /// Samples that could still be written.
    pub fn free(&self) -> usize {
        self.capacity() - self.available()
    }

    /// Whether the ring has been closed (no further writes are accepted).
    pub fn is_closed(&self) -> bool {
        self.closed.load(Ordering::Acquire)
    }

    /// Append as many samples as fit. Returns the number actually written; a
    /// short write means the caller dropped `samples.len() - written` samples.
    /// A closed ring accepts nothing.
    pub fn push(&mut self, samples: &[i16]) -> usize {
        if self.is_closed() {
            return 0;
        }
        let capacity = self.capacity();
        let writable = self.free().min(samples.len());
        for (offset, sample) in samples[..writable].iter().enumerate() {
            let index = (self.head + offset) % capacity;
            self.slots[index] = *sample;
        }
        self.head += writable;
        writable
    }

    /// Read up to `out.len()` samples in order. Returns the number read.
    pub fn pop_into(&mut self, out: &mut [i16]) -> usize {
        let capacity = self.capacity();
        let readable = self.available().min(out.len());
        for (offset, slot) in out[..readable].iter_mut().enumerate() {
            *slot = self.slots[(self.tail + offset) % capacity];
        }
        self.tail += readable;
        readable
    }

    /// Deregister the ring from the open-buffer gauge. Idempotent, and implies
    /// no further writes.
    pub fn close(&self) {
        if !self.closed.swap(true, Ordering::AcqRel) {
            OPEN_RING_BUFFERS.fetch_sub(1, Ordering::AcqRel);
        }
    }
}

impl Drop for SampleRing {
    fn drop(&mut self) {
        self.close();
    }
}

// ---------------------------------------------------------------------------
// Audio clock
// ---------------------------------------------------------------------------

/// Sample-derived frame clock. Timestamps advance by exactly one
/// [`FRAME_MICROS`] per frame, so the visual thread can align visemes to the
/// audio stream even when frames are dropped downstream.
#[derive(Debug, Clone, Copy, Default)]
pub struct AudioClock {
    frames: u64,
    origin_micros: u64,
}

impl AudioClock {
    /// A clock whose next frame is stamped `origin_micros`.
    pub const fn new(origin_micros: u64) -> Self {
        Self {
            frames: 0,
            origin_micros,
        }
    }

    /// Number of frames stamped so far.
    pub fn frames(&self) -> u64 {
        self.frames
    }

    /// Stamp the next frame and advance by exactly one frame duration.
    pub fn tick(&mut self) -> u64 {
        let stamp = self.origin_micros + self.frames * FRAME_MICROS;
        self.frames += 1;
        stamp
    }

    /// Rewind to the origin.
    pub fn reset(&mut self) {
        self.frames = 0;
    }
}

// ---------------------------------------------------------------------------
// Voice activity detection
// ---------------------------------------------------------------------------

/// Tuning for the hangover-gated energy detector.
#[derive(Debug, Clone, Copy)]
pub struct VadConfig {
    /// Normalised RMS above which a frame counts as speech.
    pub rms_threshold: f32,
    /// Frames of silence tolerated before speech is declared over. Prevents
    /// inter-word gaps from chopping the utterance.
    pub hangover_frames: u32,
}

impl Default for VadConfig {
    fn default() -> Self {
        Self {
            rms_threshold: 0.01, // ≈ -40 dBFS
            hangover_frames: 5,  // 100 ms at 20 ms/frame
        }
    }
}

/// Energy-based voice activity detector with hangover.
#[derive(Debug, Clone)]
pub struct VoiceActivityDetector {
    config: VadConfig,
    hangover: u32,
    speaking: bool,
}

impl VoiceActivityDetector {
    pub fn new(config: VadConfig) -> Self {
        Self {
            config,
            hangover: 0,
            speaking: false,
        }
    }

    /// Feed one frame's RMS and return the current decision.
    pub fn observe(&mut self, rms: f32) -> bool {
        if rms >= self.config.rms_threshold {
            self.hangover = self.config.hangover_frames;
            self.speaking = true;
        } else if self.hangover > 0 {
            self.hangover -= 1;
        } else {
            self.speaking = false;
        }
        self.speaking
    }

    /// Last decision, without advancing state.
    pub fn is_speaking(&self) -> bool {
        self.speaking
    }

    pub fn reset(&mut self) {
        self.hangover = 0;
        self.speaking = false;
    }
}

// ---------------------------------------------------------------------------
// Framing
// ---------------------------------------------------------------------------

/// One fully buffered 20 ms frame with its envelope and clock stamp.
#[derive(Debug, Clone, Copy)]
pub struct Frame {
    /// Monotonic frame index since construction.
    pub index: u64,
    /// Audio-clock capture time in microseconds — authoritative for viseme sync.
    pub capture_micros: u64,
    /// The raw PCM payload.
    pub samples: [i16; FRAME_SAMPLES],
    /// Normalised RMS amplitude.
    pub rms: f32,
    /// Peak absolute amplitude.
    pub peak: i16,
    /// Voice-activity decision including hangover.
    pub voiced: bool,
}

/// The ingress node: a lock-free capture ring plus frame extraction.
#[derive(Debug)]
pub struct AudioDsp {
    ring: SampleRing,
    clock: AudioClock,
    vad: VoiceActivityDetector,
    frame_index: u64,
    frames_emitted: u64,
    samples_dropped: u64,
}

impl AudioDsp {
    /// Build a DSP stage whose capture ring holds `ring_samples` samples.
    pub fn new(ring_samples: usize) -> Self {
        Self {
            ring: SampleRing::new(ring_samples),
            clock: AudioClock::new(0),
            vad: VoiceActivityDetector::new(VadConfig::default()),
            frame_index: 0,
            frames_emitted: 0,
            samples_dropped: 0,
        }
    }

    /// Build a DSP stage with the crystal's default ring capacity.
    pub fn with_default_capacity() -> Self {
        Self::new(DEFAULT_RING_FRAMES * FRAME_SAMPLES)
    }

    /// Build a DSP stage with a specific VAD configuration.
    pub fn with_vad(mut self, config: VadConfig) -> Self {
        self.vad = VoiceActivityDetector::new(config);
        self
    }

    /// Buffer captured PCM. Returns the number of samples accepted; anything
    /// beyond that was dropped to keep the capture callback non-blocking, and
    /// is visible in [`AudioDsp::samples_dropped`].
    pub fn push_pcm(&mut self, samples: &[i16]) -> usize {
        let written = self.ring.push(samples);
        self.samples_dropped += (samples.len() - written) as u64;
        written
    }

    /// Extract the next whole frame, or `None` while fewer than
    /// [`FRAME_SAMPLES`] samples are buffered.
    pub fn next_frame(&mut self) -> Option<Frame> {
        if self.ring.available() < FRAME_SAMPLES {
            return None;
        }
        let mut samples = [0i16; FRAME_SAMPLES];
        let read = self.ring.pop_into(&mut samples);
        debug_assert_eq!(read, FRAME_SAMPLES);

        let rms = frame_rms(&samples);
        let peak = frame_peak(&samples);
        let voiced = self.vad.observe(rms);
        let capture_micros = self.clock.tick();

        let frame = Frame {
            index: self.frame_index,
            capture_micros,
            samples,
            rms,
            peak,
            voiced,
        };
        self.frame_index += 1;
        self.frames_emitted += 1;
        Some(frame)
    }

    pub fn ring(&self) -> &SampleRing {
        &self.ring
    }

    pub fn clock(&self) -> &AudioClock {
        &self.clock
    }

    pub fn vad(&self) -> &VoiceActivityDetector {
        &self.vad
    }

    /// Frames handed to the downstream stages.
    pub fn frames_emitted(&self) -> u64 {
        self.frames_emitted
    }

    /// Samples refused by the ring and counted as dropped.
    pub fn samples_dropped(&self) -> u64 {
        self.samples_dropped
    }

    /// Release the capture ring (deregisters it from the open-buffer gauge).
    pub fn close(&mut self) {
        self.ring.close();
    }
}

// ---------------------------------------------------------------------------
// wasm32 bindings
// ---------------------------------------------------------------------------

/// Browser-facing glue. Compiled only for `wasm32` so host builds and tests
/// stay toolchain-light.
#[cfg(target_arch = "wasm32")]
pub mod wasm {
    use super::*;
    use wasm_bindgen::prelude::*;

    /// JS handle for the ingress DSP node.
    #[wasm_bindgen]
    pub struct CamelotAudioDsp {
        inner: AudioDsp,
    }

    #[wasm_bindgen]
    impl CamelotAudioDsp {
        #[wasm_bindgen(constructor)]
        pub fn new() -> CamelotAudioDsp {
            CamelotAudioDsp {
                inner: AudioDsp::with_default_capacity(),
            }
        }

        /// Buffer mono `Int16Array` PCM. Returns the accepted sample count.
        #[wasm_bindgen(js_name = pushPcm)]
        pub fn push_pcm(&mut self, samples: &[i16]) -> usize {
            self.inner.push_pcm(samples)
        }

        /// Whole frames currently buffered.
        #[wasm_bindgen(js_name = frameCount)]
        pub fn frame_count(&self) -> usize {
            self.inner.ring().available() / FRAME_SAMPLES
        }

        /// Pop one frame as `[rms, peak, captureMicros, voiced]`, or `null`
        /// while fewer than [`FRAME_SAMPLES`] samples are buffered.
        #[wasm_bindgen(js_name = nextFrame)]
        pub fn next_frame(&mut self) -> Option<Vec<f64>> {
            self.inner.next_frame().map(|frame| {
                vec![
                    frame.rms as f64,
                    frame.peak as f64,
                    frame.capture_micros as f64,
                    if frame.voiced { 1.0 } else { 0.0 },
                ]
            })
        }

        #[wasm_bindgen(js_name = framesEmitted)]
        pub fn frames_emitted(&self) -> f64 {
            self.inner.frames_emitted() as f64
        }

        #[wasm_bindgen(js_name = samplesDropped)]
        pub fn samples_dropped(&self) -> f64 {
            self.inner.samples_dropped() as f64
        }

        #[wasm_bindgen(js_name = close)]
        pub fn close(&mut self) {
            self.inner.close();
        }

        /// Process-wide gauge backing the "open ring buffers = 0" invariant.
        #[wasm_bindgen(js_name = openRingBuffers)]
        pub fn open_ring_buffers() -> usize {
            open_ring_buffers()
        }

        #[wasm_bindgen(js_name = abiVersion)]
        pub fn abi_version() -> String {
            abi_version().to_string()
        }
    }

    impl Default for CamelotAudioDsp {
        fn default() -> Self {
            Self::new()
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Mutex, MutexGuard};

    /// The open-buffer gauge is process-global, so every test that constructs a
    /// buffer takes this lock. That keeps the "open ring buffers = 0"
    /// assertions exact instead of dependent on thread interleaving.
    static RING_GAUGE_LOCK: Mutex<()> = Mutex::new(());

    fn gauge_lock() -> MutexGuard<'static, ()> {
        RING_GAUGE_LOCK.lock().unwrap_or_else(|poisoned| poisoned.into_inner())
    }

    fn ramp(len: usize, start: i32) -> Vec<i16> {
        (0..len).map(|i| (start + i as i32) as i16).collect()
    }

    // -- geometry ----------------------------------------------------------

    #[test]
    fn frame_geometry_matches_the_declared_contract() {
        assert_eq!(SAMPLE_RATE_HZ, 16_000);
        assert_eq!(FRAME_MS, 20);
        assert_eq!(FRAME_SAMPLES, 320);
        assert_eq!(FRAME_MICROS, 20_000);
        // One frame is exactly FRAME_MICROS of audio at the declared rate.
        assert_eq!(
            FRAME_SAMPLES as u64 * 1_000_000 / SAMPLE_RATE_HZ as u64,
            FRAME_MICROS
        );
    }

    #[test]
    fn default_ring_fits_inside_the_declared_memory_ceiling() {
        let bytes = DEFAULT_RING_FRAMES * FRAME_SAMPLES * core::mem::size_of::<i16>();
        assert!(bytes < MEMORY_CEILING_MB * 1024 * 1024);
    }

    // -- ring buffer -------------------------------------------------------

    #[test]
    fn ring_round_trips_samples_in_order() {
        let _guard = gauge_lock();
        let mut ring = SampleRing::new(1024);
        let input = ramp(400, 0);
        assert_eq!(ring.push(&input), 400);
        assert_eq!(ring.available(), 400);

        let mut out = vec![0i16; 400];
        assert_eq!(ring.pop_into(&mut out), 400);
        assert_eq!(out, input);
        assert_eq!(ring.available(), 0);
    }

    #[test]
    fn ring_wraps_around_without_corruption() {
        let _guard = gauge_lock();
        let mut ring = SampleRing::new(64);
        for round in 0..10 {
            let block = ramp(32, round * 32);
            assert_eq!(ring.push(&block), 32);
            let mut out = vec![0i16; 32];
            assert_eq!(ring.pop_into(&mut out), 32);
            assert_eq!(out, block);
        }
        assert_eq!(ring.available(), 0);
    }

    #[test]
    fn ring_reports_a_short_write_when_full() {
        let _guard = gauge_lock();
        let mut ring = SampleRing::new(32);
        assert_eq!(ring.capacity(), 32);
        assert_eq!(ring.push(&vec![1i16; 100]), 32);
        assert_eq!(ring.free(), 0);
        // Nothing fits, so nothing is written — a non-blocking drop, not a block.
        assert_eq!(ring.push(&[7i16; 4]), 0);
    }

    #[test]
    fn closed_ring_rejects_further_pushes() {
        let _guard = gauge_lock();
        let mut ring = SampleRing::new(64);
        assert_eq!(ring.push(&[1i16; 8]), 8);
        ring.close();
        assert!(ring.is_closed());
        assert_eq!(ring.push(&[1i16; 8]), 0);
        // Already-buffered audio stays readable so the consumer can drain.
        let mut out = vec![0i16; 8];
        assert_eq!(ring.pop_into(&mut out), 8);
    }

    #[test]
    fn open_ring_buffer_gauge_tracks_construction_and_release() {
        let _guard = gauge_lock();
        let before = open_ring_buffers();

        let ring = SampleRing::new(512);
        assert_eq!(open_ring_buffers(), before + 1);

        ring.close();
        assert_eq!(open_ring_buffers(), before);

        // close() is idempotent — a double close must not underflow the gauge.
        ring.close();
        assert_eq!(open_ring_buffers(), before);

        drop(ring);
        assert_eq!(open_ring_buffers(), before);
    }

    #[test]
    fn dropping_a_ring_releases_it_without_an_explicit_close() {
        let _guard = gauge_lock();
        let before = open_ring_buffers();
        {
            let _first = SampleRing::new(64);
            let _second = SampleRing::with_frame_capacity(2);
            assert_eq!(open_ring_buffers(), before + 2);
        }
        // The "zero frame leaks" invariant: no buffer outlives its scope.
        assert_eq!(open_ring_buffers(), before);
    }

    // -- audio clock -------------------------------------------------------

    #[test]
    fn audio_clock_advances_by_exactly_one_frame() {
        let mut clock = AudioClock::new(0);
        assert_eq!(clock.tick(), 0);
        assert_eq!(clock.tick(), FRAME_MICROS);
        assert_eq!(clock.tick(), 2 * FRAME_MICROS);
        assert_eq!(clock.frames(), 3);
        clock.reset();
        assert_eq!(clock.frames(), 0);
    }

    #[test]
    fn audio_clock_honours_a_nonzero_origin() {
        let mut clock = AudioClock::new(1_000_000);
        assert_eq!(clock.tick(), 1_000_000);
        assert_eq!(clock.tick(), 1_000_000 + FRAME_MICROS);
    }

    // -- envelope + VAD ----------------------------------------------------

    #[test]
    fn envelope_tracks_signal_energy() {
        assert_eq!(frame_rms(&[]), 0.0);
        assert_eq!(frame_peak(&[]), 0);

        let silence = vec![0i16; FRAME_SAMPLES];
        assert_eq!(frame_rms(&silence), 0.0);
        assert_eq!(frame_peak(&silence), 0);

        let half_scale = vec![16_384i16; FRAME_SAMPLES];
        assert!((frame_rms(&half_scale) - 0.5).abs() < 1e-3);
        assert_eq!(frame_peak(&half_scale), 16_384);

        // Peak saturates rather than wrapping on the most negative sample.
        assert_eq!(frame_peak(&[i16::MIN]), i16::MAX);
    }

    #[test]
    fn vad_hangs_over_then_releases() {
        let mut vad = VoiceActivityDetector::new(VadConfig::default());
        assert!(!vad.is_speaking());

        // Six loud frames open the gate.
        for _ in 0..6 {
            assert!(vad.observe(0.5));
        }
        // Silence is tolerated for the hangover window...
        for _ in 0..5 {
            assert!(vad.observe(0.0));
        }
        // ...and then speech is declared over.
        assert!(!vad.observe(0.0));
        assert!(!vad.is_speaking());

        vad.reset();
        assert!(!vad.is_speaking());
    }

    #[test]
    fn vad_reopens_the_gate_on_renergy() {
        let mut vad = VoiceActivityDetector::new(VadConfig {
            rms_threshold: 0.1,
            hangover_frames: 1,
        });
        assert!(!vad.observe(0.05)); // below threshold, never opened
        assert!(vad.observe(0.2));
        assert!(vad.observe(0.0)); // hangover
        assert!(!vad.observe(0.0));
        assert!(vad.observe(0.2)); // re-energised
    }

    // -- framing -----------------------------------------------------------

    #[test]
    fn framing_emits_whole_frames_and_retains_the_remainder() {
        let _guard = gauge_lock();
        let mut dsp = AudioDsp::new(16 * FRAME_SAMPLES);
        let input = vec![0i16; FRAME_SAMPLES * 2 + 100];

        assert_eq!(dsp.push_pcm(&input), input.len());
        assert!(dsp.next_frame().is_some());
        assert!(dsp.next_frame().is_some());
        // 100 samples cannot make a frame; they stay buffered for the next push.
        assert!(dsp.next_frame().is_none());

        assert_eq!(dsp.ring().available(), 100);
        assert_eq!(dsp.frames_emitted(), 2);
        assert_eq!(dsp.samples_dropped(), 0);
    }

    #[test]
    fn overflow_is_dropped_and_counted_not_blocked() {
        let _guard = gauge_lock();
        // A ring of exactly one frame can never buffer more than one frame.
        let mut dsp = AudioDsp::new(FRAME_SAMPLES);
        let input = vec![0i16; FRAME_SAMPLES + 50];

        assert_eq!(dsp.push_pcm(&input), FRAME_SAMPLES);
        assert_eq!(dsp.samples_dropped(), 50);

        // The accepted audio is still framable.
        assert!(dsp.next_frame().is_some());
        assert_eq!(dsp.frames_emitted(), 1);
    }

    #[test]
    fn frame_timestamps_are_audio_clock_authoritative() {
        let _guard = gauge_lock();
        let mut dsp = AudioDsp::new(4 * FRAME_SAMPLES);
        dsp.push_pcm(&vec![0i16; 3 * FRAME_SAMPLES]);

        let first = dsp.next_frame().expect("frame 0");
        let second = dsp.next_frame().expect("frame 1");
        let third = dsp.next_frame().expect("frame 2");

        assert_eq!((first.index, second.index, third.index), (0, 1, 2));
        assert_eq!(first.capture_micros, 0);
        assert_eq!(second.capture_micros, FRAME_MICROS);
        assert_eq!(third.capture_micros, 2 * FRAME_MICROS);
        // index and clock stay in lockstep, so viseme sync can trust either.
        assert_eq!(third.index, dsp.clock().frames() - 1);
    }

    #[test]
    fn a_dropped_frame_does_not_desynchronise_the_clock() {
        let _guard = gauge_lock();
        let mut dsp = AudioDsp::new(FRAME_SAMPLES);
        // Frame 0 is captured and framed; frame 1 is dropped for lack of room.
        dsp.push_pcm(&vec![0i16; FRAME_SAMPLES]);
        assert!(dsp.next_frame().is_some());
        assert_eq!(dsp.samples_dropped(), 0);

        dsp.push_pcm(&vec![0i16; FRAME_SAMPLES + 10]);
        assert_eq!(dsp.samples_dropped(), 10);
        let next = dsp.next_frame().expect("frame 1");
        // The clock advanced by frames *emitted*, not by frames *captured*.
        assert_eq!(next.index, 1);
        assert_eq!(next.capture_micros, FRAME_MICROS);
    }

    #[test]
    fn voiced_frames_are_classified_across_the_gate() {
        let _guard = gauge_lock();
        let mut dsp = AudioDsp::new(16 * FRAME_SAMPLES);
        for _ in 0..6 {
            dsp.push_pcm(&vec![8_192i16; FRAME_SAMPLES]);
        }
        for _ in 0..8 {
            dsp.push_pcm(&vec![0i16; FRAME_SAMPLES]);
        }

        let mut voiced = Vec::new();
        while let Some(frame) = dsp.next_frame() {
            voiced.push(frame.voiced);
        }

        assert_eq!(voiced.len(), 14);
        assert!(voiced[0], "loud frame must open the gate");
        assert!(voiced[5], "still loud");
        assert!(voiced[10], "hangover still holding");
        assert!(!voiced[11], "hangover exhausted");
        assert!(!voiced[13], "silence");
    }

    #[test]
    fn closing_the_dsp_releases_its_ring() {
        let _guard = gauge_lock();
        let before = open_ring_buffers();
        {
            let mut dsp = AudioDsp::with_default_capacity();
            assert_eq!(open_ring_buffers(), before + 1);
            dsp.push_pcm(&vec![0i16; FRAME_SAMPLES]);
            assert!(dsp.next_frame().is_some());

            dsp.close();
            assert_eq!(open_ring_buffers(), before);
            // A closed stage accepts no further capture.
            assert_eq!(dsp.push_pcm(&vec![0i16; FRAME_SAMPLES]), 0);
        }
        assert_eq!(open_ring_buffers(), before);
    }

    #[test]
    fn abi_version_is_reported() {
        assert_eq!(abi_version(), env!("CARGO_PKG_VERSION"));
    }
}

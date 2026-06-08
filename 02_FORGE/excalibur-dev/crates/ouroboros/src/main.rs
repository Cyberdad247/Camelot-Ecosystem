use excalibur_ouroboros::OuroborosEngine;
use serde::{Deserialize, Serialize};
use std::io::{self, Read};
use std::time::Instant;
use uuid::Uuid;

// ---------------------------------------------------------------------------
// Wire protocol — JSON in via stdin, JSON out via stdout.
// Called by the Next.js Route Handler via child_process.spawn.
// ---------------------------------------------------------------------------

#[derive(Deserialize)]
struct Request {
    intent:    String,
    #[serde(default = "default_state_dim")]
    state_dim: usize,
}

fn default_state_dim() -> usize { 256 }

#[derive(Serialize)]
struct Response {
    ast_json:   String,
    latency_ms: f64,
}

#[derive(Serialize)]
struct AstNode {
    id:    String,
    pid:   Option<String>,
    tag:   String,
    props: AstProps,
}

#[derive(Serialize)]
struct AstProps {
    intent:     String,
    confidence: f32,
    variant:    &'static str,
}

// ---------------------------------------------------------------------------
// Component tag vocabulary — mapped from intent keywords then SSM logit.
// ---------------------------------------------------------------------------

const VOCAB: &[(&str, &[&str])] = &[
    ("hero",        &["hero", "banner", "header", "headline", "landing", "above"]),
    ("nav",         &["nav", "navigation", "menu", "header", "bar"]),
    ("features",    &["feature", "benefit", "why", "what", "capability"]),
    ("testimonial", &["testimonial", "review", "quote", "customer", "trust"]),
    ("pricing",     &["pricing", "price", "plan", "tier", "cost", "subscription"]),
    ("gallery",     &["gallery", "image", "photo", "portfolio", "showcase"]),
    ("cta",         &["cta", "call", "action", "button", "sign", "get", "start", "buy"]),
    ("contact",     &["contact", "form", "email", "reach", "touch"]),
    ("footer",      &["footer", "bottom", "links", "legal"]),
    ("card",        &["card", "item", "product", "article", "post"]),
];

fn keyword_tag(intent: &str) -> Option<&'static str> {
    let lower = intent.to_lowercase();
    for (tag, keywords) in VOCAB {
        if keywords.iter().any(|kw| lower.contains(kw)) {
            return Some(tag);
        }
    }
    None
}

fn logit_tag(logit: f32) -> &'static str {
    // Map logit [-1, 1] onto the vocabulary index deterministically.
    let idx = ((logit + 1.0) / 2.0 * VOCAB.len() as f32).abs() as usize;
    VOCAB[idx.min(VOCAB.len() - 1)].0
}

fn logit_variant(logit: f32) -> &'static str {
    match logit {
        v if v > 0.5  => "bold",
        v if v > 0.0  => "standard",
        v if v > -0.5 => "minimal",
        _              => "ghost",
    }
}

// ---------------------------------------------------------------------------
// Simple tokenizer — hash each word to a u32 token id.
// ---------------------------------------------------------------------------

fn tokenize(text: &str) -> Vec<u32> {
    text.split_whitespace()
        .map(|word| {
            word.bytes().fold(2166136261u32, |acc, b| {
                acc.wrapping_mul(16777619).wrapping_add(b as u32)
            })
        })
        .collect()
}

fn main() -> anyhow::Result<()> {
    let t0 = Instant::now();

    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;

    let req: Request = serde_json::from_str(input.trim())
        .map_err(|e| anyhow::anyhow!("bad stdin JSON: {e}"))?;

    let engine = OuroborosEngine::new(req.state_dim);
    let mut state = engine.initial_state();

    let tokens = tokenize(&req.intent);
    let mut last_logit = 0.0f32;

    for token in tokens {
        last_logit = engine.step(&mut state, token)?;
    }

    let tag      = keyword_tag(&req.intent).unwrap_or_else(|| logit_tag(last_logit));
    let variant  = logit_variant(last_logit);
    let confidence = (last_logit.abs()).min(1.0);

    let node = AstNode {
        id:  Uuid::new_v4().to_string(),
        pid: None,
        tag: tag.to_string(),
        props: AstProps {
            intent: req.intent.clone(),
            confidence,
            variant,
        },
    };

    let response = Response {
        ast_json:   serde_json::to_string(&node)?,
        latency_ms: t0.elapsed().as_secs_f64() * 1000.0,
    };

    println!("{}", serde_json::to_string(&response)?);
    Ok(())
}

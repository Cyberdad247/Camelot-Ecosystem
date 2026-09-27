import { motion } from 'framer-motion';

export default function GravityAnchor() {
  return (
    <section className="relative min-h-screen w-full flex items-center bg-[#4A0404] text-[#C0C0C0] overflow-hidden">
      {/* Texture Layer */}
      <div className="absolute inset-0 opacity-30 bg-[url('/assets/cracked-earth.jpg')] mix-blend-multiply" />

      <div className="container mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-12 items-center relative z-10">
        {/* The Portrait */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 1 }}
          className="relative group"
        >
          <div className="absolute -inset-4 bg-gradient-to-r from-[#FF4500] to-transparent opacity-20 blur-xl group-hover:opacity-40 transition-opacity" />
          <img
            src="/assets/vashawn-head-bw.jpg"
            alt="VaShawn F. Head - CEO"
            className="relative rounded-sm border-l-4 border-[#FF4500] shadow-2xl grayscale contrast-125 hover:grayscale-0 transition-all duration-700"
          />
        </motion.div>

        {/* The Narrative */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          <div className="flex items-center gap-4 mb-6">
            <span className="h-[2px] w-12 bg-[#FF4500]" />
            <h3 className="font-mono text-sm tracking-widest text-[#FF4500] uppercase">
              1971: The Crucible
            </h3>
          </div>

          <h2 className="text-5xl font-serif font-bold text-white mb-8 leading-tight">
            Forged in the <br />
            <span className="italic text-[#C0C0C0]">Santa Line Slaying</span>
          </h2>

          <p className="text-lg leading-relaxed text-[#a8a8a8] mb-6">
            Before the philosophy, there was the fracture. Witnessing the chaos at Higbee&apos;s
            department store wasn&apos;t just a memory—it was the initial code break.
          </p>
          <p className="text-lg leading-relaxed text-[#a8a8a8]">
            For 55 years, I have processed the <strong>&quot;Illusion&quot;</strong> of control.
            This platform is the result of that defragmentation.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

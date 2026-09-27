import { motion } from 'framer-motion';
import { useFireTrail } from '../hooks/useFireTrail';

const poems = [
  { id: 1, title: 'Fragment 01', text: 'Before the logic / There was the noise...' },
  { id: 2, title: 'The Santa Line', text: '1971 cracked the lens / I saw the code beneath.' },
  { id: 3, title: 'Defrag', text: 'Deleting the ghost files / To find the machine.' },
];

export default function RawDataArchive() {
  const { fireGlow } = useFireTrail();

  return (
    <section className="relative h-screen flex flex-col justify-center items-center bg-[#1a0505] overflow-hidden">
      {/* Background Texture: Torn Paper Effect */}
      <div className="absolute inset-0 bg-[url('/assets/texture-grain.png')] opacity-20 mix-blend-overlay" />

      <div className="z-10 w-full max-w-6xl px-4">
        <h2 className="mb-12 text-center font-serif text-4xl text-[#C0C0C0]">
          THE RAW DATA{' '}
          <span className="text-xs font-mono tracking-widest text-[#FF4500]">[UNPROCESSED]</span>
        </h2>

        {/* 3D Carousel Container */}
        <div className="flex gap-8 overflow-x-auto pb-10 snap-x snap-mandatory scrollbar-hide">
          {poems.map((poem, index) => (
            <motion.div
              key={poem.id}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              style={{ boxShadow: fireGlow }} // The Fire Trail illuminates the cards
              className="snap-center min-w-[300px] md:min-w-[400px] bg-[#e3d5c6] text-black p-8 rounded-sm rotate-1 hover:rotate-0 transition-transform duration-500"
            >
              <div className="border-b-2 border-black/10 pb-4 mb-4 flex justify-between items-center">
                <span className="font-mono text-xs text-red-800">FIG_{poem.id}</span>
                <span className="font-serif italic font-bold">{poem.title}</span>
              </div>
              <p className="font-mono text-sm leading-relaxed whitespace-pre-line">{poem.text}</p>
              <div className="mt-6 flex justify-end">
                <div className="h-8 w-8 rounded-full border border-black/20 flex items-center justify-center">
                  ➜
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

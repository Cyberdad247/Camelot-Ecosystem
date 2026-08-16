import { motion } from 'framer-motion';

const products = [
  { id: 1, name: 'OILS: ESSENCE', price: '$45', desc: 'Biological Fuel', col: 'col-span-2' },
  { id: 2, name: 'CANDLE: VOID', price: '$32', desc: 'Burn the Illusion', col: 'col-span-1' },
  { id: 3, name: 'JEWELRY: ARMOR', price: '$120', desc: 'Sovereign Adornment', col: 'col-span-3' },
];

export default function AlchemyLab() {
  return (
    <section className="relative min-h-screen py-24 bg-[#050505] border-t border-[#00FF99]/20">
      {/* Interstellar Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-[#00FF99]/5 via-[#050505] to-[#050505]" />

      <div className="container mx-auto px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h2 className="text-6xl font-serif text-transparent bg-clip-text bg-gradient-to-b from-white to-[#00FF99]">
            THE ALCHEMY LAB
          </h2>
          <p className="font-mono text-[#00FF99] mt-4 tracking-widest">
            [ HEADARTWORKS.COM INTEGRATION ]
          </p>
        </motion.div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {products.map((item) => (
            <motion.a
              href="https://www.headartworks.com"
              target="_blank"
              key={item.id}
              className={`${item.col} group relative h-[400px] overflow-hidden rounded-xl border border-[#00FF99]/30 bg-[#0a0a0a] hover:border-[#00FF99] transition-colors`}
              whileHover={{ scale: 0.98 }}
              rel="noreferrer"
            >
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80" />

              {/* Product Info */}
              <div className="absolute bottom-0 left-0 p-8 w-full">
                <div className="flex justify-between items-end border-b border-[#00FF99] pb-4 mb-4 transform translate-y-4 group-hover:translate-y-0 transition-transform">
                  <h3 className="text-3xl font-bold text-white">{item.name}</h3>
                  <span className="font-mono text-[#00FF99] text-xl">{item.price}</span>
                </div>
                <p className="font-mono text-sm text-[#C0C0C0] opacity-0 group-hover:opacity-100 transition-opacity">
                  [STATUS]: {item.desc} // READY_TO_SHIP
                </p>
              </div>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  );
}

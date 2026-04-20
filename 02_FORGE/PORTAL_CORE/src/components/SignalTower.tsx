import { ArrowRight } from 'lucide-react';

export default function SignalTower() {
    return (
        <section className="h-[80vh] flex flex-col justify-center items-center bg-[#000] relative overflow-hidden">
            {/* The Singularity Light Source */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[2px] h-full bg-gradient-to-b from-[#00FF99] to-transparent blur-[2px]" />

            <div className="z-10 text-center max-w-2xl px-6">
                <h2 className="text-4xl md:text-5xl font-serif text-white mb-6">
                    Secure Your Seat on the Flight.
                </h2>
                <p className="text-[#C0C0C0] mb-10 font-mono text-sm">
          // DEFRAG YOUR HISTORY. TRANSCEND THE ILLUSION.
                </p>

                <form className="flex flex-col md:flex-row gap-4 w-full" onSubmit={(e) => e.preventDefault()}>
                    <input
                        type="email"
                        placeholder="ENTER_FREQUENCY_ID (EMAIL)"
                        className="flex-1 bg-[#111] border border-[#333] text-[#00FF99] px-6 py-4 rounded-lg focus:outline-none focus:border-[#00FF99] font-mono placeholder:text-[#444]"
                    />
                    <button type="submit" className="group bg-[#00FF99] text-black px-8 py-4 rounded-lg font-bold tracking-wider hover:bg-white transition-colors flex items-center justify-center gap-2">
                        ENGAGE
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                </form>

                <p className="mt-8 text-xs text-[#444] font-mono">
                    [SYSTEM]: NO SPAM PERMITTED BY TITANIUM LAW.
                </p>
            </div>
        </section>
    );
}

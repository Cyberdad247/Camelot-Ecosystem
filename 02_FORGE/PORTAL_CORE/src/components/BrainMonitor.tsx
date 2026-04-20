import React from 'react';

interface BrainMonitorProps {
    currentOp?: {
        source: 'LOCAL' | 'CLOUD' | 'IDLE';
        cost: string;
    };
    networkStatus: 'EARTH' | 'SKY' | 'OFFLINE';
}

export const BrainMonitor = ({ currentOp = { source: 'IDLE', cost: '0.00' }, networkStatus }: BrainMonitorProps) => {
    return (
        <div className="flex gap-2 p-2 bg-black border-t border-green-900 select-none">

            {/* NETWORK STATUS */}
            <div className="flex flex-col items-center justify-center mr-4 border-r border-green-900 pr-4">
                <span className="text-[8px] text-gray-500">LINK:</span>
                <span className={`text-[10px] font-bold ${networkStatus === 'EARTH' ? 'text-green-500' : networkStatus === 'SKY' ? 'text-blue-500' : 'text-red-500'}`}>
                    {networkStatus}
                </span>
            </div>

            {/* MORGANA (Local) INDICATOR */}
            <div className={`flex flex-col items-center transition-opacity duration-300 ${currentOp.source === 'LOCAL' ? 'opacity-100' : 'opacity-30'}`}>
                <div className={`h-2 w-2 rounded-full ${currentOp.source === 'LOCAL' ? 'bg-green-500 animate-pulse' : 'bg-green-900'}`} />
                <span className="text-[10px] text-green-500 font-bold">MORGANA</span>
                <span className="text-[8px] text-gray-500">Local</span>
            </div>

            {/* MERLIN (Cloud) INDICATOR */}
            <div className={`flex flex-col items-center transition-opacity duration-300 ${currentOp.source === 'CLOUD' ? 'opacity-100' : 'opacity-30'}`}>
                <div className={`h-2 w-2 rounded-full ${currentOp.source === 'CLOUD' ? 'bg-purple-500 animate-pulse' : 'bg-purple-900'}`} />
                <span className="text-[10px] text-purple-500 font-bold">MERLIN</span>
                <span className="text-[8px] text-gray-500">Modal</span>
            </div>

            {/* COST METER */}
            <div className="ml-auto flex flex-col items-end justify-center">
                <span className="text-[10px] text-yellow-500 font-mono">
                    ${currentOp.cost}
                </span>
                <span className="text-[8px] text-gray-600">EST. COST</span>
            </div>

        </div>
    );
};

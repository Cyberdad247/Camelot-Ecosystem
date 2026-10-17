import React, { useState, useRef, useEffect } from 'react';
import { cn } from '../../lib/utils';
import { triggerHaptic } from '../../lib/haptics';

export interface CommandInputProps {
  value?: string;
  onChange?: (val: string) => void;
  onSubmit?: (cmd: string) => void;
  placeholder?: string;
  className?: string;
  suggestions?: string[];
}

const DEFAULT_RUNES = [
  '//STATUS',
  '//FORGE',
  '//SWARM',
  '//SCAN',
  '//PLAN',
  '//HEAL',
  '//BOOT',
  '//CONTEXT',
  '//CLOUDBRAIN',
  '//ENGAGE_BIFROST',
  'Omega_Helios',
  'Omega_Boris',
  'Omega_Codex',
  'Omega_Sentinel',
  'Omega_Jev',
];

export const CommandInput = ({
  value: controlledValue,
  onChange,
  onSubmit,
  placeholder = 'Enter runic command (//STATUS, //FORGE, //SCAN)...',
  className,
  suggestions = DEFAULT_RUNES,
}: CommandInputProps) => {
  const [internalValue, setInternalValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const currentValue = controlledValue !== undefined ? controlledValue : internalValue;

  const filteredSuggestions = suggestions.filter((s) =>
    s.toLowerCase().includes(currentValue.trim().toLowerCase())
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (controlledValue === undefined) {
      setInternalValue(val);
    }
    onChange?.(val);
    setShowSuggestions(val.length > 0 && filteredSuggestions.length > 0);
    setSelectedIndex(0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (showSuggestions && filteredSuggestions.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredSuggestions.length);
        triggerHaptic('tick');
        return;
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredSuggestions.length) % filteredSuggestions.length);
        triggerHaptic('tick');
        return;
      }
      if (e.key === 'Tab') {
        e.preventDefault();
        const selected = filteredSuggestions[selectedIndex];
        if (selected) {
          applySuggestion(selected);
        }
        return;
      }
    }

    if (e.key === 'Enter') {
      e.preventDefault();
      if (showSuggestions && filteredSuggestions.length > 0 && selectedIndex >= 0) {
        applySuggestion(filteredSuggestions[selectedIndex]);
      } else {
        submitCommand(currentValue);
      }
    }

    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const applySuggestion = (suggestion: string) => {
    triggerHaptic('tap');
    if (controlledValue === undefined) {
      setInternalValue(suggestion);
    }
    onChange?.(suggestion);
    setShowSuggestions(false);
    submitCommand(suggestion);
  };

  const submitCommand = (cmd: string) => {
    if (!cmd.trim()) return;
    triggerHaptic('success');
    onSubmit?.(cmd.trim());
    if (controlledValue === undefined) {
      setInternalValue('');
    }
    onChange?.('');
    setShowSuggestions(false);
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (inputRef.current && !inputRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={cn('relative w-full', className)}>
      <div className="relative flex items-center">
        {/* Terminal prompt symbol */}
        <span className="absolute left-3.5 text-[#D4AF37] font-mono text-sm pointer-events-none select-none">
          ⚡
        </span>
        <input
          ref={inputRef}
          type="text"
          value={currentValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            'w-full bg-[#050510]/85 border border-[#D4AF37]/40 rounded-lg pl-9 pr-10 py-2.5',
            'font-mono text-sm text-[#F1EFF4] placeholder:text-[#9E9AA7]/50',
            'focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]',
            'shadow-[0_0_20px_rgba(212,175,55,0.1)] transition-all min-h-[44px]'
          )}
        />
        {currentValue && (
          <button
            type="button"
            onClick={() => {
              if (controlledValue === undefined) setInternalValue('');
              onChange?.('');
              inputRef.current?.focus();
            }}
            className="absolute right-3 text-[#9E9AA7] hover:text-white text-xs font-mono p-1"
          >
            ✕
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <ul
          role="listbox"
          className="absolute z-50 w-full mt-1.5 bg-[#050510]/95 border border-[#D4AF37]/50 rounded-lg shadow-[0_8px_30px_rgba(0,0,0,0.8)] backdrop-blur-xl max-h-56 overflow-y-auto overflow-x-hidden p-1 font-mono text-xs"
        >
          {filteredSuggestions.map((suggestion, idx) => (
            <li
              key={suggestion}
              role="option"
              aria-selected={idx === selectedIndex}
              onMouseEnter={() => setSelectedIndex(idx)}
              onClick={() => applySuggestion(suggestion)}
              className={cn(
                'px-3 py-2 rounded cursor-pointer flex items-center justify-between transition-colors min-h-[36px]',
                idx === selectedIndex
                  ? 'bg-[#D4AF37]/20 text-[#D4AF37] border-l-2 border-[#D4AF37]'
                  : 'text-[#F1EFF4]/80 hover:bg-white/5'
              )}
            >
              <span>{suggestion}</span>
              <span className="text-[10px] text-[#9E9AA7]/50 uppercase">Tab ⏎</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

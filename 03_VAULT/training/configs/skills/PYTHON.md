# Skill: Python (SIR_KINETIC)
# Loaded dynamically when agent touches .py files

## Stack
- FastAPI with CORSMiddleware (origins=["*"] for dev)
- Modal.com for serverless GPU compute
- Heavy deps lazy-loaded inside functions (prevent local OOM)
- Async endpoints with polling loops (while + time.sleep)

## Constraints
- 8GB RAM ceiling enforced by Rotel
- 4-bit quantization: BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")
- max_memory={0: "6GB"}, offload_folder="/tmp/offload"
- Flash attention enabled when NVIDIA GPU detected

## Patterns
- Pydantic models for all I/O boundaries
- MLflow autolog() for experiment tracking
- DSPy Signatures for programmatic prompt optimization

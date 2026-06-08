use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn deterministic_soul_score(seed: &str) -> u32 {
    seed.bytes().fold(2_166_136_261_u32, |hash, byte| {
        (hash ^ u32::from(byte)).wrapping_mul(16_777_619)
    })
}

#[wasm_bindgen]
pub fn execute_soul_algorithm(seed: &str) -> String {
    format!("camelot:{:08x}", deterministic_soul_score(seed))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn algorithm_is_deterministic() {
        assert_eq!(deterministic_soul_score("camelot"), deterministic_soul_score("camelot"));
        assert!(execute_soul_algorithm("camelot").starts_with("camelot:"));
    }
}

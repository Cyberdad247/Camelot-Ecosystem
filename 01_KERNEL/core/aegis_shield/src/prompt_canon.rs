use serde_json::{Map, Value};
use unicode_normalization::UnicodeNormalization;

pub fn normalize_prompt_text(input: &str) -> String {
    input.nfc().collect::<String>().trim().to_string()
}

pub fn canonicalize_json_value(value: &Value) -> Value {
    match value {
        Value::Array(items) => Value::Array(items.iter().map(canonicalize_json_value).collect()),
        Value::Object(map) => {
            let mut sorted = Map::new();
            let mut keys: Vec<&String> = map.keys().collect();
            keys.sort();
            for key in keys {
                if let Some(value) = map.get(key) {
                    sorted.insert(key.clone(), canonicalize_json_value(value));
                }
            }
            Value::Object(sorted)
        }
        Value::String(text) => Value::String(normalize_prompt_text(text)),
        _ => value.clone(),
    }
}

pub fn compile_tool_schema(schema: &Value) -> Result<String, serde_json::Error> {
    serde_json::to_string(&canonicalize_json_value(schema))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn canonical_schema_orders_keys_and_normalizes_text() {
        let schema = json!({"z": " cafe\u{301} ", "a": {"b": 2}});
        let compiled = compile_tool_schema(&schema).unwrap();
        assert_eq!(compiled, "{\"a\":{\"b\":2},\"z\":\"caf\u{e9}\"}");
    }
}

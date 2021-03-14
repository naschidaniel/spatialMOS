use std::collections::HashMap;

// print out hello world
pub fn rs_hello_world(name: &str) -> String {
    format!("Hello {}! This message comes from Rust.", name)
}

pub fn rs_convert_datetime() -> String {
    let mut measurements = HashMap::new();

    measurements.insert(
        "date".to_string(),
        "2021-01-01T23:00:00CET".to_string(),
    );
    
    format!("{}", measurements["date"])
}
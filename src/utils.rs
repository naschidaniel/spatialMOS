use std::collections::HashMap;

// print out hello world
pub fn rs_hello_world(name: &str) -> String {
    format!("Hello {}! This message comes from Rust.", name)
}


pub fn rs_convert_datetime() -> String {
    let mut measurements = HashMap::new();


    //'2021-01-01T23:00:00CET': {'date': '2021-01-01T23:00:00CET', 'name': '82500WS', 'lat': 46.6156, 'lon': 11.4604, 'alt': 2260, 'LF': 100.5}, 
    //'2021-01-01T22:00:00CET': {'date': '2021-01-01T22:00:00CET', 'name': '82500WS', 'lat': 46.6156, 'lon': 11.4604, 'alt': 2260, 'LF': 100.5}, 

    measurements.insert(
        "date".to_string(),
        "2021-01-01T23:00:00CET".to_string(),
    );
    
    format!("{}", measurements["date"])
}
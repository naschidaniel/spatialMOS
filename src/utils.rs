use std::collections::HashMap;
use chrono::{DateTime, TimeZone, NaiveDateTime, Utc, Local};

// print out hello world
pub fn rs_hello_world(name: &str) -> String {
    format!("Hello {}! This message comes from Rust.", name)
}

pub fn rs_convert_datetime() -> String {
    let mut measurements = HashMap::new();

    let dt = DateTime::<Utc>::from_utc(NaiveDateTime::from_timestamp(61, 0), Utc);
    assert_eq!(Utc.timestamp(61, 0), dt);
    //'2021-01-01T23:00:00CET': {'date': '2021-01-01T23:00:00CET', 'name': '82500WS', 'lat': 46.6156, 'lon': 11.4604, 'alt': 2260, 'LF': 100.5},
    //'2021-01-01T22:00:00CET': {'date': '2021-01-01T22:00:00CET', 'name': '82500WS', 'lat': 46.6156, 'lon': 11.4604, 'alt': 2260, 'LF': 100.5},

    let utc = Utc::now();
    let local = Local::now();
    let datum = "2021-01-01T23:00:00CET".replace("CET", "+01:00").replace("CEST", "+02:00");
    measurements.insert("date", &datum);

    let converted = DateTime::parse_from_rfc3339(&datum).unwrap();
    let utc_converted: DateTime<Utc> = DateTime::from(converted);
    let utc_converted_str = DateTime::format(&utc_converted, "%Y-%m-%d %H:%M:%S");
    println!("{:?}", converted);
    println!("{:?}", utc_converted);
    println!("{}", utc_converted_str);

    format!("{}", measurements["date"])
}

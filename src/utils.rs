use chrono::{DateTime, Utc};
use pyo3::prelude::*;

pub fn rs_convert_datetime(date: &str, _utc: DateTime<Utc>) -> String {
    let converted = DateTime::parse_from_rfc3339(&date).unwrap();
    let utc_converted: DateTime<Utc> = DateTime::from(converted);
    format!("{}", DateTime::format(&utc_converted, "%Y-%m-%d %H:%M:%S"))
}

pub fn log_py_error(err: PyErr) {
    println!("{:?}", err)
}

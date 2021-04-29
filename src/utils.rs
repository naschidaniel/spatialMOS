use chrono::{DateTime, Utc};
use pyo3::prelude::*;
use math::round;

pub fn rs_convert_datetime(date: &str, _utc: DateTime<Utc>) -> String {
    let converted = DateTime::parse_from_rfc3339(&date).unwrap();
    let utc_converted: DateTime<Utc> = DateTime::from(converted);
    format!("{}", DateTime::format(&utc_converted, "%Y-%m-%d %H:%M:%S"))
}

pub fn log_spr(spread: &f64) -> f64 { 
    if spread > &0. {
        return round::half_away_from_zero(spread.log(2.7182818), 2);
    }
    return 0.
} 


pub fn rs_combine_gribdata<'a>(latitudes: &'a Vec<f64>, longitudes: &'a Vec<f64>, values_avg: &'a Vec<Vec<f64>>, values_spr: &'a Vec<Vec<f64>>, values_log_spr: &'a Vec<Vec<f64>>) -> Vec<[&'a f64; 5]> {
  
    let mut data = Vec::new();
    for (i, latitude) in latitudes.iter().enumerate() {
        for (j,longitude) in longitudes.iter().enumerate() {
            data.push([latitude, longitude, &values_spr[i][j], &values_log_spr[i][j], &values_avg[i][j]]);
        }
    }
    data
}

pub fn log_py_error(err: PyErr) {
    println!("{:?}", err)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_log_spr_ok() {
        assert_eq!(1.1, log_spr(&3.))
    }

    #[test]
    fn test_log_spr_zero_ok() {
        assert_eq!(0., log_spr(&0.))
    }

    #[test]
    fn test_log_spr_minus_ok() {
        assert_eq!(0., log_spr(&-1.))
    }
}
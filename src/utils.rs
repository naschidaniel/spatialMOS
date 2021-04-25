use chrono::{DateTime, Utc};
use pyo3::prelude::*;
use math::round;

pub fn rs_convert_datetime(date: &str, _utc: DateTime<Utc>) -> String {
    let converted = DateTime::parse_from_rfc3339(&date).unwrap();
    let utc_converted: DateTime<Utc> = DateTime::from(converted);
    format!("{}", DateTime::format(&utc_converted, "%Y-%m-%d %H:%M:%S"))
}

fn log_spr(spread: &f64) -> f64 { 
    if spread > &&0. {
        return round(spread.log(10.), 3)
    }
    return 0.
} 


pub fn rs_combine_gribdata(latitudes: Vec<f64>, longitudes: Vec<f64>, values_avg: Vec<[f64; 3]>, values_spr: Vec<[f64; 3]>) {
    let mut values_log_spr = values_spr.clone();
    // values_log_spr.into_iter().for_each(|f| f.into_iter().map(|x| x.log(10.)));
    
    for entry in values_log_spr.iter_mut() {
        entry.into_iter().map(|x| log_spr(x));
    }
    
    let mut data = Vec::new();
    for (i, latitude) in latitudes.iter().enumerate() {
        for (j,longitude) in longitudes.iter().enumerate() {
            data.push([latitude, longitude, &values_spr[i][j], &values_log_spr[i][j], &values_avg[i][j]]);
        }
    }

    // for (i, entry) in data.into_iter().enumerate() {
    //     match i {
            
    //     } 
    //     let rudi = entry.iter().map(|x| x.log(10.)).collect::<Vec<_>>();
    //     println!("{:?}", rudi);
    // }
}

pub fn log_py_error(err: PyErr) {
    println!("{:?}", err)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_log_spr_ok() {
        assert_eq!(0.477, log_spr(&3.))
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
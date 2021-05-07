mod utils;
mod bilinear_interpolation;

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::wrap_pyfunction;
use pyo3::Python;

#[pyfunction]
fn combine_gribdata(
    py_latitudes: &PyList,
    py_longitudes: &PyList,
    py_values_avg: &PyList,
    py_values_spr: &PyList,
) -> PyResult<PyObject>{
    let gil = Python::acquire_gil();
    let py = gil.python();

    let latitudes = py_latitudes.extract()?;
    let longitudes = py_longitudes.extract()?;
    let values_avg= py_values_avg.extract()?;
    let values_spr: Vec<Vec<f64>> = py_values_spr.extract()?;
    let mut values_log_spr = values_spr.clone();

    for x in values_log_spr.iter_mut() {
        for i in x.iter_mut() {
            *i = utils::log_spr(i);
        }
    }

    let data = utils::rs_combine_gribdata(
        &latitudes,
        &longitudes,
        &values_avg,
        &values_spr,
        &values_log_spr,
    );
    Ok(data.into_py(py))
}

#[pyfunction]
fn convert_measurements(measurements: &PyDict, columns: &PyList) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let utc = Utc::now();
    let dates = measurements.keys();
    let measurements_write_lines = PyList::empty(py);
    match columns.del_item(0) {
        Err(err) => utils::log_py_error(err),
        _ => (),
    }
    for date in dates {
        let values: &PyDict = measurements.get_item(&date).unwrap().downcast().unwrap();
        let date_str = &date
            .to_string()
            .replace("CET", "+01:00")
            .replace("CEST", "+02:00");
        let row = PyList::empty(py);

        row.append(utils::rs_convert_datetime(&date_str, utc))
            .map_err(|err| utils::log_py_error(err))
            .ok();
        for column in columns {
            let value = values.get_item(&column);
            row.append(value)
                .map_err(|err| utils::log_py_error(err))
                .ok();
        }
        measurements_write_lines
            .append(row)
            .map_err(|err| utils::log_py_error(err))
            .ok();
    }
    Ok(measurements_write_lines.into())
}

#[pyfunction]
fn interpolate_gribdata() -> PyResult<()>{  
    let gil = Python::acquire_gil();
    let _py = gil.python();
    
    let grid_data = bilinear_interpolation::Grid {
        p11: bilinear_interpolation::Point{x: 0., y: 0., value: 0.}, 
        p12: bilinear_interpolation::Point{x: 0., y: 1., value: 1.},
        p21: bilinear_interpolation::Point{x: 1., y: 0., value: 1.},
        p22: bilinear_interpolation::Point{x: 1., y: 1., value: 1.},
    };
    
    assert_eq!(0.75 , bilinear_interpolation::rs_bilinear_interpolate_point(0.5, 0.5, grid_data));

    Ok(())
}

/// A python module implemented in Rust for spatialMOS.
#[pymodule]
fn spatial_rust_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(combine_gribdata, m)?)?;
    m.add_function(wrap_pyfunction!(convert_measurements, m)?)?;
    m.add_function(wrap_pyfunction!(interpolate_gribdata, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rs_date_hashmap() {
        let utc = Utc::now();
        assert_eq!(
            "2021-03-17 23:00:00",
            utils::rs_convert_datetime("2021-03-18T00:00:00+01:00", utc)
        );
        assert_eq!(
            "2021-03-28 00:00:00",
            utils::rs_convert_datetime("2021-03-28T02:00:00+02:00", utc)
        );
    }

    #[test]
    fn test_rs_combine_gribdata() {
        let latitude = vec![45.0, 45.5, 46.0];
        let longitude = vec![8.0, 8.5, 9.0];
        let values_avg = vec![
            vec![4.600, 4.300, 3.270],
            vec![2.660, 4.830, 5.820],
            vec![-8.550, -0.610, -0.410],
        ];
        let values_spr = vec![vec![0.24, 0.27, 0.32], vec![0.19, 0.18, 0.14], vec![0.87, 0.18, 0.15]];
        let mut values_log_spr = values_spr.clone();

        for x in values_log_spr.iter_mut() {
            for i in x.iter_mut() {
                *i = utils::log_spr(i);
            }
        }
        let data = utils::rs_combine_gribdata(
            &latitude,
            &longitude,
            &values_avg,
            &values_spr,
            &values_log_spr,
        );

        let combined_ok = vec![
            [&45.0, &8.0, &0.24, &-1.43, &4.6],
            [&45.0, &8.5, &0.27, &-1.31, &4.3],
            [&45.0, &9.0, &0.32, &-1.14, &3.27],
            [&45.5, &8.0, &0.19, &-1.66, &2.66],
            [&45.5, &8.5, &0.18, &-1.71, &4.83],
            [&45.5, &9.0, &0.14, &-1.97, &5.82],
            [&46.0, &8.0, &0.87, &-0.14, &-8.55],
            [&46.0, &8.5, &0.18, &-1.71, &-0.61],
            [&46.0, &9.0, &0.15, &-1.9, &-0.41],
        ];
        assert_eq!(combined_ok, data)
    }
}

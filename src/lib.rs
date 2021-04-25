mod utils;

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::wrap_pyfunction;
use pyo3::Python;

#[pyfunction]
fn combine_gribdata(
    values_avg: &PyList,
    values_spr: &PyList,
    latitudes: &PyList,
    longitudes: &PyList,
) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();
    let data = PyList::empty(py);

    let mut i = 0;
    let mut j = 0;
    let _values_avg_vec: Vec<f32> = values_avg.extract()?;

    for latitude in latitudes {
        j = 0;
        let row = PyList::empty(py);
        for longitude in longitudes {
            j += 1;
            let v = vec![latitude, longitude, values_avg.get_item(i)];
            row.append(v).map_err(|err| utils::log_py_error(err)).ok();
            println!("{}", row);
        }
        data.append(row)
            .map_err(|err| utils::log_py_error(err))
            .ok();

        i += 1;
    }
    Ok(data.into())
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

/// A python module implemented in Rust for spatialMOS.
#[pymodule]
fn spatial_rust_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(combine_gribdata, m)?)?;
    m.add_function(wrap_pyfunction!(convert_measurements, m)?)?;
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
            [4.600, 4.300, 3.270],
            [2.660, 4.830, 5.820],
            [-8.550, -0.610, -0.410],
        ];
        let values_spr = vec![
            [0.24, 0.27, 0.32],
            [0.19, 0.18, 0.14],
            [0.87, 0.18, 0.15],
            ];
        utils::rs_combine_gribdata(latitude, longitude, values_avg, values_spr);
    }
}

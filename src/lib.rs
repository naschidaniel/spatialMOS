mod utils;

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::wrap_pyfunction;
use pyo3::Python;

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
fn spatial_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(convert_measurements, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rs_date_hashmap() {
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
}

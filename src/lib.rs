mod utils;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

/// print out a dict
#[pyfunction]
fn hello_world(msg: &str) -> PyResult<String> {
    let greeting = utils::rs_hello_world(msg);
    Ok(greeting)
}

/// A python module implemented in Rust for spatialMOS.
#[pymodule]
fn spatial_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_world, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rs_date_hashmap() {
        assert_eq!("2021-01-01T23:00:00CET", utils::rs_convert_datetime());
    }

    #[test]
    fn greeting_contains_name() {
        assert_eq!("Hello Daniel! This message comes from Rust.", utils::rs_hello_world("Daniel"));
    }
}
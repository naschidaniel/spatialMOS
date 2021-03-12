use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

// 
fn rs_hello_world(name: &str) -> String {
    format!("Hello {}! This message comes from Rust.", name)
}

/// print out a dict
#[pyfunction]
fn hello_world(msg: &str) -> PyResult<String> {
    let greeting = rs_hello_world(msg);
    Ok(greeting)
}

/// A python module implemented in Rust for spatialMOS.
#[pymodule]
fn spatial_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_world, m)?)?;
    Ok(())
}
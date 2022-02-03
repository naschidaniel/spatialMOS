mod bilinear_interpolation;
mod utils;

use chrono::Utc;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::wrap_pyfunction;
use pyo3::Python;
use std::collections::HashMap;

#[pyfunction]
fn combine_nwp_climatology(
    py_gfse_data: &PyList,
    py_measurements: &PyList,
) -> PyResult<Vec<[String; 9]>> {
    let gfse_data: Vec<Vec<String>> = py_gfse_data.extract()?;
    let gfse_data_len = gfse_data.len();
    let measurements: Vec<Vec<String>> = py_measurements.extract()?;
    let mut nwp_climatology = Vec::new();
    let mut measurements_hashmap = HashMap::new();

    for row in measurements.iter() {
        let key = vec![row[0].clone(), row[2].clone(), row[3].clone()].join("_");
        measurements_hashmap.insert(
            key,
            row
        );
    }

    for (i, row) in gfse_data.iter().enumerate() {
        let quot = i / (gfse_data_len / 10);
        let rem = i % (gfse_data_len / 10);

        if rem == 0 {
            println!("Done {} percent", quot * 10);
        }
        let gfse_data_key = vec![row[1].clone(), row[5].clone(), row[6].clone()].join("_");
        if measurements_hashmap.contains_key(&gfse_data_key) {
            let alt = measurements_hashmap[&gfse_data_key][1].clone();
            let lon = measurements_hashmap[&gfse_data_key][2].clone();
            let lat = measurements_hashmap[&gfse_data_key][3].clone();
            let obs = measurements_hashmap[&gfse_data_key][4].clone();
            let yday = row[2].clone();
            let kfold = String::from("1");
            let dayminute = row[3].clone();
            let mean = row[9].clone();
            let log_spread = row[8].clone();
            nwp_climatology.push([yday, kfold, dayminute, alt, lon, lat, obs, mean, log_spread]);
        }
    }
    Ok(nwp_climatology)
}

#[pyfunction]
fn combine_gribdata(
    py_latitudes: &PyList,
    py_longitudes: &PyList,
    py_values_avg: &PyList,
    py_values_spr: &PyList,
) -> PyResult<PyObject> {
    let gil = Python::acquire_gil();
    let py = gil.python();

    let latitudes = py_latitudes.extract()?;
    let longitudes = py_longitudes.extract()?;
    let values_avg = py_values_avg.extract()?;
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
fn get_value_from_gribdata(
    py_latitudes: &PyList,
    py_longitudes: &PyList,
    py_values: &PyList,
    x: f64,
    y: f64,
) -> PyResult<f64> {
    let latitudes: Vec<f64> = py_latitudes.extract()?;
    let longitudes: Vec<f64> = py_longitudes.extract()?;
    let values: Vec<Vec<f64>> = py_values.extract()?;

    let x1_index = longitudes.iter().position(|&lon| lon == x).unwrap();
    let y1_index = latitudes.iter().position(|&lat| lat == y).unwrap();

    let value = values[y1_index][x1_index];
    Ok(value.into())
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
fn interpolate_gribdata(
    py_latitudes: &PyList,
    py_longitudes: &PyList,
    py_values_avg: &PyList,
    py_values_spr: &PyList,
    py_stations: &PyList,
) -> PyResult<Vec<Vec<f64>>> {
    let latitudes: Vec<f64> = py_latitudes.extract()?;
    let longitudes: Vec<f64> = py_longitudes.extract()?;
    let values_avg: Vec<Vec<f64>> = py_values_avg.extract()?;
    let values_spr: Vec<Vec<f64>> = py_values_spr.extract()?;
    let mut stations: Vec<Vec<f64>> = py_stations.extract()?;

    let resolution = latitudes[0] - latitudes[1];
    for station in stations.iter_mut() {
        // station[0] = lon
        // station[1] = lat
        let x_select = station[0] - station[0] % resolution;
        let y_select = station[1] - station[1] % resolution;

        let x1_index = longitudes.iter().position(|&lon| lon == x_select).unwrap();
        let y1_index = latitudes.iter().position(|&lat| lat == y_select).unwrap();

        let bilinear_data = bilinear_interpolation::BiLinearData {
            x1: longitudes[x1_index],
            x2: longitudes[x1_index + 1],
            y1: latitudes[y1_index],
            y2: latitudes[y1_index + 1],
            v_avg_11: values_avg[y1_index][x1_index],
            v_avg_12: values_avg[y1_index + 1][x1_index],
            v_avg_21: values_avg[y1_index][x1_index + 1],
            v_avg_22: values_avg[y1_index + 1][x1_index + 1],
            v_spr_11: values_spr[y1_index][x1_index],
            v_spr_12: values_spr[y1_index + 1][x1_index],
            v_spr_21: values_spr[y1_index][x1_index + 1],
            v_spr_22: values_spr[y1_index + 1][x1_index + 1],
        };
        let mut data = bilinear_interpolation::rs_bilinear_interpolate_point(
            station[0],
            station[1],
            bilinear_data,
        );
        let log_spr = utils::log_spr(&data[0]);
        data.insert(1, log_spr);
        station.append(&mut data)
    }
    Ok(stations.into())
}

/// A python module implemented in Rust for spatialMOS.
#[pymodule]
fn spatial_rust_util(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(combine_nwp_climatology, m)?)?;
    m.add_function(wrap_pyfunction!(combine_gribdata, m)?)?;
    m.add_function(wrap_pyfunction!(convert_measurements, m)?)?;
    m.add_function(wrap_pyfunction!(interpolate_gribdata, m)?)?;
    m.add_function(wrap_pyfunction!(get_value_from_gribdata, m)?)?;
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
        let values_spr = vec![
            vec![0.24, 0.27, 0.32],
            vec![0.19, 0.18, 0.14],
            vec![0.87, 0.18, 0.15],
        ];
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

mod utils;

use std::collections::HashMap;

fn main() {
    println!("{}", utils::rs_convert_datetime());
    println!("{}", utils::rs_hello_world("Daniel"));

    let mut hm = HashMap::new();
    for i in 1..5 {
        hm.insert(i + i, i * i);
    }
    println!("{:?}", hm);
}

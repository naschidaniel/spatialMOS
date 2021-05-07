use math::round;

pub struct Point {
    pub x: f64,
    pub y: f64,
    pub value: f64,
}

pub struct Grid {
    pub p11: Point,
    pub p12: Point,
    pub p21: Point,
    pub p22: Point,
}

// rs_bilinear_interpolate_point approximates the value at the point f(x,y)
pub fn rs_bilinear_interpolate_point(x: f64, y: f64, grid: Grid) -> f64 {
    // Implementation as described in https://en.wikipedia.org/wiki/Bilinear_interpolation#Algorithm
    // Q12(x1,y2) -- Q22(x2,y2)
    //    |             |
    //    |    f(x,y)   |
    //    |             |
    // Q11(x1,y1) -- Q21(x2,y1)    
    
    let x1 = grid.p11.x;
    let x2 = grid.p21.x;
    let y1 = grid.p11.y;
    let y2 = grid.p22.y;

    let fxy1 = (x2 - x) / (x2 - x1) * grid.p11.value + (x - x1) / (x2 - x1) * grid.p21.value;
    let fxy2 = (x2 - x) / (x2 - x1) * grid.p12.value + (x - x1) / (x2 - x1) * grid.p22.value;
    let fxy = (y2 - y) / (y2 - y1) * fxy1 + (y - y1) / (y2 - y1) * fxy2;
    round::half_away_from_zero(fxy, 2)
}



#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test0_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 0., y: 0., value: 0.}, 
            p12: Point{x: 0., y: 1., value: 1.},
            p21: Point{x: 1., y: 0., value: 1.},
            p22: Point{x: 1., y: 1., value: 0.},
        };
        
        assert_eq!(0.5, rs_bilinear_interpolate_point(0.5, 0.5, grid_data))
    }

    #[test]
    fn test1_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 0., y: 0., value: 0.}, 
            p12: Point{x: 0., y: 1., value: 1.},
            p21: Point{x: 1., y: 0., value: 0.},
            p22: Point{x: 1., y: 1., value: 1.},
        };
        
        assert_eq!(0.5, rs_bilinear_interpolate_point(0.5, 0.5, grid_data))
    }

    #[test]
    fn test2_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 0., y: 0., value: 1.}, 
            p12: Point{x: 0., y: 1., value: 1.},
            p21: Point{x: 1., y: 0., value: 1.},
            p22: Point{x: 1., y: 1., value: 1.},
        };
        
        assert_eq!(1., rs_bilinear_interpolate_point(0.5, 0.5, grid_data))
    }

    #[test]
    fn test3_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 0., y: 0., value: 0.}, 
            p12: Point{x: 0., y: 1., value: 1.},
            p21: Point{x: 1., y: 0., value: 0.},
            p22: Point{x: 1., y: 1., value: 1.},
        };
        
        assert_eq!(0.7, rs_bilinear_interpolate_point(0.7, 0.7, grid_data))
    }

    #[test]
    fn test4_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 0., y: 0., value: 0.}, 
            p12: Point{x: 0., y: 1., value: 1.},
            p21: Point{x: 1., y: 0., value: 1.},
            p22: Point{x: 1., y: 1., value: 1.},
        };
        
        assert_eq!(0.75 , rs_bilinear_interpolate_point(0.5, 0.5, grid_data))
    }

    #[test]
    fn test5_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 0., y: 0., value: 0.}, 
            p12: Point{x: 0., y: 1., value: 1.},
            p21: Point{x: 1., y: 0., value: 1.},
            p22: Point{x: 1., y: 1., value: 1.},
        };
        
        assert_eq!(0.75 , rs_bilinear_interpolate_point(0.5, 0.5, grid_data))
    }

    #[test]
    fn test6_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point{x: 14., y: 20., value: 91.}, 
            p12: Point{x: 14., y: 21., value: 162.},
            p21: Point{x: 15., y: 20., value: 210.},
            p22: Point{x: 15., y: 21., value: 95.},
        };
        
        assert_eq!(146.1, rs_bilinear_interpolate_point(14.5, 20.2, grid_data))
    }
}


use math::round;

pub struct BiLinearData {
    pub x1: f64,
    pub x2: f64,
    pub y1: f64,
    pub y2: f64,
    pub v_avg_11: f64,
    pub v_avg_12: f64,
    pub v_avg_21: f64,
    pub v_avg_22: f64,
    pub v_spr_11: f64,
    pub v_spr_12: f64,
    pub v_spr_21: f64,
    pub v_spr_22: f64,
}

// rs_bilinear_interpolate_point approximates the value at the point f(x,y)

pub fn rs_bilinear_interpolate_point(x: f64, y: f64, data: BiLinearData) -> Vec<f64> {
    // Implementation as described in https://en.wikipedia.org/wiki/Bilinear_interpolation#Algorithm
    // Q12(x1,y2,v12) -- Q22(x2,y2,v22)
    //    |                 |
    //    |    f(x,y,vxy)   |
    //    |                 |
    // Q11(x1,y1,v11) -- Q21(x2,y1,v21)

    let f_avg_xy1 = (data.x2 - x) / (data.x2 - data.x1) * data.v_avg_11
        + (x - data.x1) / (data.x2 - data.x1) * data.v_avg_21;
    let f_avg_xy2 = (data.x2 - x) / (data.x2 - data.x1) * data.v_avg_12
        + (x - data.x1) / (data.x2 - data.x1) * data.v_avg_22;
    let v_avg_xy = (data.y2 - y) / (data.y2 - data.y1) * f_avg_xy1
        + (y - data.y1) / (data.y2 - data.y1) * f_avg_xy2;

    let f_spr_xy1 = (data.x2 - x) / (data.x2 - data.x1) * data.v_spr_11
        + (x - data.x1) / (data.x2 - data.x1) * data.v_spr_21;
    let f_spr_xy2 = (data.x2 - x) / (data.x2 - data.x1) * data.v_spr_12
        + (x - data.x1) / (data.x2 - data.x1) * data.v_spr_22;
    let v_spr_xy = (data.y2 - y) / (data.y2 - data.y1) * f_spr_xy1
        + (y - data.y1) / (data.y2 - data.y1) * f_spr_xy2;

    // python implementation ... first spr then avg
    vec![
        round::half_away_from_zero(v_spr_xy, 2),
        round::half_away_from_zero(v_avg_xy, 2),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    struct Point {
        pub x: f64,
        pub y: f64,
        pub v_avg: f64,
        pub v_spr: f64,
    }

    struct Grid {
        pub p11: Point,
        pub p12: Point,
        pub p21: Point,
        pub p22: Point,
    }

    fn rs_build_bilinear_data(grid_data: Grid) -> BiLinearData {
        BiLinearData {
            x1: grid_data.p11.x,
            x2: grid_data.p21.x,
            y1: grid_data.p11.y,
            y2: grid_data.p22.y,
            v_avg_11: grid_data.p11.v_avg,
            v_avg_12: grid_data.p12.v_avg,
            v_avg_21: grid_data.p21.v_avg,
            v_avg_22: grid_data.p22.v_avg,
            v_spr_11: grid_data.p11.v_spr,
            v_spr_12: grid_data.p12.v_spr,
            v_spr_21: grid_data.p21.v_spr,
            v_spr_22: grid_data.p22.v_spr,
        }
    }
    #[test]
    fn test0_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point {
                x: 0.,
                y: 0.,
                v_avg: 0.,
                v_spr: 0.,
            },
            p12: Point {
                x: 0.,
                y: 1.,
                v_avg: 1.,
                v_spr: 1.,
            },
            p21: Point {
                x: 1.,
                y: 0.,
                v_avg: 1.,
                v_spr: 1.,
            },
            p22: Point {
                x: 1.,
                y: 1.,
                v_avg: 0.,
                v_spr: 0.,
            },
        };
        let bilinear_data = rs_build_bilinear_data(grid_data);
        assert_eq!(
            vec![0.5, 0.5],
            rs_bilinear_interpolate_point(0.5, 0.5, bilinear_data)
        )
    }

    #[test]
    fn test1_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point {
                x: 0.,
                y: 0.,
                v_avg: 0.,
                v_spr: 0.,
            },
            p12: Point {
                x: 0.,
                y: 1.,
                v_avg: 1.,
                v_spr: 0.,
            },
            p21: Point {
                x: 1.,
                y: 0.,
                v_avg: 1.,
                v_spr: 1.,
            },
            p22: Point {
                x: 1.,
                y: 1.,
                v_avg: 1.,
                v_spr: 1.,
            },
        };

        let bilinear_data = rs_build_bilinear_data(grid_data);
        assert_eq!(
            vec![0.5, 0.75],
            rs_bilinear_interpolate_point(0.5, 0.5, bilinear_data)
        )
    }

    #[test]
    fn test2_rs_bilinear_interpolate_point_ok() {
        let grid_data = Grid {
            p11: Point {
                x: 14.,
                y: 20.,
                v_avg: 91.,
                v_spr: 91.,
            },
            p12: Point {
                x: 14.,
                y: 21.,
                v_avg: 162.,
                v_spr: 162.,
            },
            p21: Point {
                x: 15.,
                y: 20.,
                v_avg: 210.,
                v_spr: 210.,
            },
            p22: Point {
                x: 15.,
                y: 21.,
                v_avg: 95.,
                v_spr: 95.,
            },
        };

        let bilinear_data = rs_build_bilinear_data(grid_data);
        assert_eq!(
            vec![146.1, 146.1],
            rs_bilinear_interpolate_point(14.5, 20.2, bilinear_data)
        )
    }
}

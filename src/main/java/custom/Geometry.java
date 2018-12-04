package custom;

import java.lang.Math;

public class Geometry {
	private static final double R = 50;
	private static final double v = 1.5;
	
	public static double rho(int num) {
		return 218.89233 * Math.pow(num, -0.569877);
	}
	
	public static double absError(double e, int num, double T) {
		double r = rho(num), vT = v*T, l = r + vT;
		if (R < 2*l + vT) return Double.POSITIVE_INFINITY;
		double rmin = vT * (R - 2*vT) / (R + 2*vT);
		if (r < rmin) r = rmin;
		return (1+e) * R / (R - 2*l);
	}

	public static double relError(double e, int num, double T) {
		double r = rho(num), vT = v*T, l = r + vT;
		if (R < 2*l + 2*vT) return Double.POSITIVE_INFINITY;
		double rmin = vT * (Math.sqrt((R - vT)*(R + vT/2)) - vT) / (R + vT);
		if (r < rmin) r = rmin;
		return (1+e) * Math.max(R / (R - 2*l), R / (R - vT) * (R + l*vT/r) / (R - l - vT/2));
	}
}

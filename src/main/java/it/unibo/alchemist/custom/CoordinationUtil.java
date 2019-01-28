package it.unibo.alchemist.custom;

import org.protelis.lang.datatype.Tuple;

import it.unibo.alchemist.model.implementations.positions.LatLongPosition;
import it.unibo.alchemist.model.interfaces.GeoPosition;
import it.unibo.alchemist.protelis.AlchemistExecutionContext;
import java8.util.Objects;

public class CoordinationUtil {
    
    public static double computeDistance(AlchemistExecutionContext<GeoPosition> context, Tuple target) {
        if (Objects.requireNonNull(target).size() == 2) {
            final Object lat = target.get(0);
            final Object lon = target.get(1);
            if (lat instanceof Double && lon instanceof Double) {
                return context.getDevicePosition().getDistanceTo(new LatLongPosition((Double) lat, (Double) lon));
            }
        }
        throw new IllegalArgumentException("Not a position: " + target);
    }

}

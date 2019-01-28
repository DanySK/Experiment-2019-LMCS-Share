package it.unibo.alchemist.custom;

import org.protelis.lang.datatype.Tuple;

import it.unibo.alchemist.model.implementations.positions.Euclidean2DPosition;
import it.unibo.alchemist.model.implementations.positions.LatLongPosition;
import it.unibo.alchemist.model.interfaces.GeoPosition;
import it.unibo.alchemist.model.interfaces.Position;
import it.unibo.alchemist.protelis.AlchemistExecutionContext;
import java.util.Objects;

public class CoordinationUtil {
    
    public static <P extends Position<P>> double computeDistance(AlchemistExecutionContext<P> context, Tuple target) {
        if (Objects.requireNonNull(target).size() == 2) {
            final Object lat = target.get(0);
            final Object lon = target.get(1);
            if (lat instanceof Double && lon instanceof Double) {
                final P myPosition = context.getDevicePosition();
                if (myPosition instanceof GeoPosition) {
                    return ((GeoPosition) myPosition).getDistanceTo(new LatLongPosition((Double) lat, (Double) lon));
                } else if (myPosition instanceof Euclidean2DPosition){
                    return ((Euclidean2DPosition) myPosition).getDistanceTo(new Euclidean2DPosition((Double) lat, (Double) lon));
                } else {
                    throw new IllegalStateException("Unknown position type: " + myPosition.getClass().getSimpleName());
                }
            }
        }
        throw new IllegalArgumentException("Not a position: " + target);
    }

}

package it.unibo.alchemist.model.implementations.terminators;

import java.util.function.Predicate;
import it.unibo.alchemist.model.interfaces.Environment;

public class Terminator<T> implements Predicate<Environment<T>> {
	private final double finalTime;
	
	public Terminator(double finalTime) {
		this.finalTime = finalTime;
	}
	
	@Override
	public boolean test(Environment<T> environment) {
		return environment.getSimulation().getTime().toDouble() > finalTime;
	}
}

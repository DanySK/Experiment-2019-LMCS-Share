package it.unibo.alchemist.loader.export;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.DoubleStream;

import org.apache.commons.math3.stat.descriptive.UnivariateStatistic;

import com.google.common.collect.ImmutableList;

import it.unibo.alchemist.model.interfaces.Environment;
import it.unibo.alchemist.model.interfaces.Node;
import it.unibo.alchemist.model.interfaces.Reaction;
import it.unibo.alchemist.model.interfaces.Time;

/**
 * Reads the value of a molecule and logs it.
 * 
 * @param <T>
 */
public abstract class AggregableExtractor implements Extractor {

    private final List<UnivariateStatistic> aggregators;
    private final ImmutableList<String> columns;
    private final FilteringPolicy filter;

    /**
     * @param molecule
     *            the target molecule
     * @param property
     *            the target property
     * @param incarnation
     *            the target incarnation
     * @param filter
     *            the {@link FilteringPolicy} to use
     * @param aggregators
     *            the names of the {@link UnivariateStatistic} to use for
     *            aggregating data. If an empty list is passed, then the values
     *            will be logged indipendently for each node.
     */
    public AggregableExtractor(final FilteringPolicy filter, final List<String> aggregators, final String name) {
        this.filter = Objects.requireNonNull(filter);
        this.aggregators = Objects.requireNonNull(aggregators).parallelStream()
                .map(StatUtil::makeUnivariateStatistic)
                .filter(Optional::isPresent)
                .map(Optional::get)
                .collect(Collectors.toList());
        this.columns = this.aggregators.isEmpty()
                    ? ImmutableList.of(name + "@every_node")
                    : this.aggregators.stream()
                        .map(Object::getClass)
                        .map(Class::getSimpleName)
                        .map(aggregator -> name + '[' + aggregator + ']')
                        .collect(ImmutableList.toImmutableList());
    }

    @Override
    public final <T> double[] extractData(final Environment<T> env, final Reaction<T> r, final Time time, final long step) {
        final DoubleStream values = valueStream(env, r, time, step);
        if (aggregators.isEmpty()) {
            return values.toArray();
        } else {
            final double[] input = values.flatMap(filter::apply).toArray();
            if (input.length == 0) {
                final double[] result = new double[aggregators.size()];
                Arrays.fill(result, Double.NaN);
                return result;
            }
            return aggregators.stream()
                    .mapToDouble(a -> a.evaluate(input))
                    .toArray();
        }
    }
    
    protected <T> DoubleStream valueStream(final Environment<T> env, final Reaction<T> r, final Time time, final long step) {
        return env.getNodes().stream().mapToDouble(n -> extractOnNode(env, n, r, time, step));
    }
    
    protected abstract <T> double extractOnNode(final Environment<T> env, final Node<T> n, final Reaction<T> r, final Time time, final long step);

    @Override
    public final List<String> getNames() {
        return columns;
    }

}

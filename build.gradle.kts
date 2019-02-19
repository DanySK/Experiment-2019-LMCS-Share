import org.gradle.internal.impldep.org.apache.commons.io.output.ByteArrayOutputStream
import org.jetbrains.kotlin.gradle.tasks.KotlinCompile
import org.apache.tools.ant.taskdefs.condition.Os
import org.codehaus.groovy.ast.tools.GeneralUtils.args

plugins {
    java
    eclipse
    kotlin("jvm") version "1.3.11"
}

group = "it.unibo.alchemist"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    maven("https://dl.bintray.com/alchemist-simulator/Alchemist/")
    maven("https://dl.bintray.com/protelis/Protelis/")
}

dependencies {
    api("it.unibo.alchemist:alchemist:8.0.0-beta+0sr.822ad")
    implementation(kotlin("stdlib-jdk8"))
}

configure<JavaPluginConvention> {
    sourceCompatibility = JavaVersion.VERSION_1_8
}
tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "1.8"
}

sourceSets.getByName("main") {
    resources {
        srcDirs("src/main/protelis")
    }
}

task("runTests") {
    doLast {
        println("Done.")
    }
}
fun makeTest(
    file: String,
    name: String = file,
    sampling: Double = 1.0,
    time: Double = Double.POSITIVE_INFINITY,
    vars: Set<String> = setOf(),
    maxHeap: Long? = null,
    taskSize: Int = 512,
    threads: Int? = null,
    debug: Boolean = false
) {
    val heap: Long = maxHeap ?: if (System.getProperty("os.name").toLowerCase().contains("linux")) {
        ByteArrayOutputStream().use { output ->
                exec {
                    executable = "bash"
                    args = listOf("-c", "cat /proc/meminfo | grep MemAvailable | grep -o '[0-9]*'")
                    standardOutput = output
                }
                output.toString().trim().toLong() / 1024
            }
            .also { println("Detected ${it}MB RAM available.") }  * 9 / 10
    } else {
        // Guess 16GB RAM of which 2 used by the OS
        14 * 1024L
    }
    val threadCount = threads ?: maxOf(1, minOf(Runtime.getRuntime().availableProcessors(), heap.toInt() / taskSize ))
    println("Running on $threadCount threads")
    task<JavaExec>("$name") {
        classpath = sourceSets["main"].runtimeClasspath
        classpath("src/main/protelis")
        main = "it.unibo.alchemist.Alchemist"
        maxHeapSize = "${heap}m"
        if (debug) {
            jvmArgs("-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=1044")
        }
        File("data").mkdirs()
        args(
            "-y", "src/main/yaml/${file}.yml",
            "-t", "$time",
            "-e", "data/${name}",
            "-p", threadCount,
            "-i", "$sampling"
        )
        if (vars.isNotEmpty()) {
            args("-b", "-var", *vars.toTypedArray())
        }
    }
    tasks {
        "runTests" {
            dependsOn("$name")
        }
    }
}

makeTest("s1_corridor", name = "corridor", sampling = 2.0, time = 500.0, vars = setOf("seed"))

defaultTasks("runTests")

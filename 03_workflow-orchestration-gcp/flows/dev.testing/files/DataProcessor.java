import java.io.*;
import java.util.*;

public class DataProcessor {
    public static void main(String[] args) throws IOException {
        // Read input
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "Diana");
        
        // Process data
        System.out.println("Processing " + names.size() + " records...");
        
        // Write output
        try (PrintWriter writer = new PrintWriter("output.txt")) {
            for (String name : names) {
                writer.println(name.toUpperCase());
            }
        }
        
        System.out.println("✓ Processing complete!");
        System.out.println("Output saved to output.txt");
    }
}
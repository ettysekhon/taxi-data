package com.example;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.*;
import java.util.*;

public class DataProcessor {
    
    public static void main(String[] args) throws IOException {
        System.out.println("Starting Data Processor...");
        
        // Create sample data
        List<Person> people = Arrays.asList(
            new Person("Alice", 25, "Engineering"),
            new Person("Bob", 30, "Sales"),
            new Person("Charlie", 35, "Marketing")
        );
        
        // Process data using external library (Gson)
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String json = gson.toJson(people);
        
        // Write output
        try (PrintWriter writer = new PrintWriter("output.json")) {
            writer.println(json);
        }
        
        // Generate summary
        double avgAge = people.stream()
            .mapToInt(Person::getAge)
            .average()
            .orElse(0);
        
        System.out.println("✓ Processed " + people.size() + " records");
        System.out.println("✓ Average age: " + String.format("%.1f", avgAge));
        System.out.println("✓ Output saved to output.json");
    }
    
    static class Person {
        private String name;
        private int age;
        private String department;
        
        public Person(String name, int age, String department) {
            this.name = name;
            this.age = age;
            this.department = department;
        }
        
        public int getAge() { return age; }
    }
}
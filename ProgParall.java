// MatrixVectorProduct.java
// Program to multiply a large matrix A by a vector x, with A and x read from files.
import java.io.*;
import java.util.*;

public class MatrixVectorProduct {

    public static void main(String[] args) {
        try {
            // Read matrix A from file
            double[][] matrixA = readMatrixFromFile("matrix.txt");

            // Read vector x from file
            double[] vectorX = readVectorFromFile("vector.txt");

            // Validate dimensions
            if (matrixA[0].length != vectorX.length) {
                throw new IllegalArgumentException("Matrix columns and vector size do not match.");
            }

            // Perform matrix-vector multiplication
            double[] result = multiplyMatrixByVector(matrixA, vectorX);

            // Print the result
            System.out.println("Resulting vector:");
            for (double val : result) {
                System.out.println(val);
            }

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }

    // Reads a matrix from a file
    private static double[][] readMatrixFromFile(String fileName) throws IOException {
        List<double[]> matrix = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.trim().split(" ");
                double[] row = Arrays.stream(parts).mapToDouble(Double::parseDouble).toArray();
                matrix.add(row);
            }
        }
        return matrix.toArray(new double[0][]);
    }

    // Reads a vector from a file
    private static double[] readVectorFromFile(String fileName) throws IOException {
        List<Double> vector = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            while ((line = br.readLine()) != null) {
                vector.add(Double.parseDouble(line.trim()));
            }
        }
        return vector.stream().mapToDouble(Double::doubleValue).toArray();
    }

    // Multiplies a matrix by a vector
    private static double[] multiplyMatrixByVector(double[][] matrix, double[] vector) {
        int rows = matrix.length;
        int cols = vector.length;
        double[] result = new double[rows];

        for (int i = 0; i < rows; i++) {
            double sum = 0;
            for (int j = 0; j < cols; j++) {
                sum += matrix[i][j] * vector[j];
            }
            result[i] = sum;
        }

        return result;
    }
}

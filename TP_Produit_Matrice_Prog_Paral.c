#include <mpi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define M 4 // Nombre de lignes de A
#define N 4 // Nombre de colonnes de A et de lignes de B
#define P 4 // Nombre de colonnes de B

void lire_matrice(const char *fichier, double matrice[][N], int lignes, int colonnes)
{
    FILE *fp = fopen(fichier, "r");
    if (fp == NULL)
    {
        fprintf(stderr, "Erreur : Impossible d'ouvrir le fichier %s\n", fichier);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    for (int i = 0; i < lignes; i++)
    {
        for (int j = 0; j < colonnes; j++)
        {
            if (fscanf(fp, "%lf", &matrice[i][j]) != 1)
            {
                fprintf(stderr, "Erreur : Format incorrect dans le fichier %s\n", fichier);
                fclose(fp);
                MPI_Abort(MPI_COMM_WORLD, 1);
            }
        }
    }
    fclose(fp);
}

int main(int argc, char **argv)
{
    int rank, size, i, j, k;

    double A[M][N], B[N][P], C[M][P] = {0};
    double local_A[M / 4][N];

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size != M)
    {
        if (rank == 0)
        {
            fprintf(stderr, "Ce programme nécessite %d processus MPI.\n", M);
        }
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    if (rank == 0)
    {
        printf("Lecture des matrices depuis les fichiers...\n");
        lire_matrice("A.txt", A, M, N);
        lire_matrice("B.txt", B, N, P);
    }

    MPI_Bcast(B, N * P, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    MPI_Scatter(A, M / size * N, MPI_DOUBLE, local_A, M / size * N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
  
    for (i = 0; i < M / size; i++)
    {
        for (j = 0; j < P; j++)
        {
            for (k = 0; k < N; k++)
            {
                C[i + rank * (M / size)][j] += local_A[i][k] * B[k][j];
            }
        }
    }

    MPI_Gather(C + rank * (M / size) * P, M / size * P, MPI_DOUBLE,
               C, M / size * P, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (rank == 0)
    {
        printf("Résultat : Matrice C\n");
        FILE *fp = fopen("C.txt", "w");
        if (fp == NULL)
        {
            fprintf(stderr, "Erreur : Impossible d'écrire le fichier de sortie C.txt\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
        for (i = 0; i < M; i++)
        {
            for (j = 0; j < P; j++)
            {
                fprintf(fp, "%d ", (int)C[i][j]);
                printf("%d ", (int)C[i][j]);
            }
            fprintf(fp, "\n");
            printf("\n");
        }
        fclose(fp);
        printf("Matrice C sauvegardée dans le fichier C.txt\n");
    }

    MPI_Finalize();
    return 0;
}

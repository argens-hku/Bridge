#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <iterator>
#include <algorithm>
#include <vector>
#include <random>
#include "../include/dll.h"

//g++ -o3 -flto -std=c++11 -c MakeHands.cpp -o MakeHands.o
//g++ -o3 -flto -mtune=generic -L. -l dds MakeHands.o -o MakeHands

// #define no_of_hands 1000

#define DDS_FULL_LINE 80
#define DDS_HAND_OFFSET 12
#define DDS_HAND_LINES 12

unsigned char dcardRank[16] =
{ 
  'x', 'x', '2', '3', '4', '5', '6', '7',
  '8', '9', 'T', 'J', 'Q', 'K', 'A', '-'
};

unsigned short int dbitMapRank[16] =
{
  0x0000, 0x0000, 0x0001, 0x0002, 0x0004, 0x0008, 0x0010, 0x0020,
  0x0040, 0x0080, 0x0100, 0x0200, 0x0400, 0x0800, 0x1000, 0x2000
};

unsigned char dcardSuit[5] = { 'S', 'H', 'D', 'C', 'N' };
unsigned char dcardHand[4] = { 'N', 'E', 'S', 'W' };

struct card
{
  int suit;
  int cards;
};

std::vector <card> deck = {
  {0,14},{0,2},{0,3},{0,4},{0,5},{0,6},{0,7},{0,8},{0,9},{0,10},{0,11},{0,12},{0,13},
  {1,14},{1,2},{1,3},{1,4},{1,5},{1,6},{1,7},{1,8},{1,9},{1,10},{1,11},{1,12},{1,13},
  {2,14},{2,2},{2,3},{2,4},{2,5},{2,6},{2,7},{2,8},{2,9},{2,10},{2,11},{2,12},{2,13},
  {3,14},{3,2},{3,3},{3,4},{3,5},{3,6},{3,7},{3,8},{3,9},{3,10},{3,11},{3,12},{3,13}
};

void gen_hand (unsigned int deal [][DDS_SUITS], std::mt19937 g)
{
  for (int h = 0; h < DDS_HANDS; h++){
    for (int s = 0; s < DDS_SUITS; s++){
      deal [h][s] = 0;
    } 
  }

  int h;
  unsigned u;

  std::shuffle (deck.begin(), deck.end(), g);
  int count = 0;
  for (auto it : deck)
  {
    h = (int) count / 13;
    // printf ("%d\n", h);
    u = dbitMapRank [it.cards] << 2;
    deal [h][it.suit] |= u;
    count ++;
  }
}

void PrintHand(char title[],
               unsigned int remainCards[DDS_HANDS][DDS_SUITS])
{
  int c, h, s, r;
  char text[DDS_HAND_LINES][DDS_FULL_LINE];

  for (int l = 0; l < DDS_HAND_LINES; l++)
  {
    memset(text[l], ' ', DDS_FULL_LINE);
    text[l][DDS_FULL_LINE - 1] = '\0';
  }

  for (h = 0; h < DDS_HANDS; h++)
  {
    int offset, line;
    if (h == 0)
    {
      offset = DDS_HAND_OFFSET;
      line = 0;
    }
    else if (h == 1)
    {
      offset = 2 * DDS_HAND_OFFSET;
      line = 4;
    }
    else if (h == 2)
    {
      offset = DDS_HAND_OFFSET;
      line = 8;
    }
    else
    {
      offset = 0;
      line = 4;
    }

    for (s = 0; s < DDS_SUITS; s++)
    {
      c = offset;
      for (r = 14; r >= 2; r--)
      {
        if ((remainCards[h][s] >> 2) & dbitMapRank[r])
          text[line + s][c++] = static_cast<char>(dcardRank[r]);
      }

      if (c == offset)
        text[line + s][c++] = '-';

      if (h != 3)
        text[line + s][c] = '\0';
    }
  }
  printf("%s", title);
  char dashes[80];
  int l = static_cast<int>(strlen(title)) - 1;
  for (int i = 0; i < l; i++)
    dashes[i] = '-';
  dashes[l] = '\0';
  printf("%s\n", dashes);
  for (int i = 0; i < DDS_HAND_LINES; i++)
    printf("%s\n", text[i]);
  printf("\n\n");
}

void PrintTable(ddTableResults * table)
{
  printf("%5s %-5s %-5s %-5s %-5s\n",
         "", "North", "South", "East", "West");

  printf("%5s %5d %5d %5d %5d\n",
         "NT",
         table->resTable[4][0],
         table->resTable[4][2],
         table->resTable[4][1],
         table->resTable[4][3]);

  for (int suit = 0; suit < DDS_SUITS; suit++)
  {
    printf("%5c %5d %5d %5d %5d\n",
           dcardSuit[suit],
           table->resTable[suit][0],
           table->resTable[suit][2],
           table->resTable[suit][1],
           table->resTable[suit][3]);
  }
  printf("\n");
}

// bool CompareTable(ddTableResults * table, int handno)
// {
//   for (int suit = 0; suit < DDS_STRAINS; suit++)
//   {
//     for (int pl = 0; pl <= 3; pl++)
//     {
//       if (table->resTable[suit][pl] != DDtable[handno][4 * suit + pl])
//         return false;
//     }
//   }
//   return true;
// }

// void PrintHandToFile (unsigned int cards[DDS_HANDS][DDS_SUITS], std::ofstream fout){
//   for (int h = 0; h < DDS_HANDS; h++){
//     for (int s = 0; s < DDS_SUITS; s++){
//       fout << cards [h][s];
//     }
//   }
// }
// void PrintTableToFile (ddTableResults * table, std::ofstream fout){
//   for (int s = 0; s < DDS_STRAINS; s++){
//     for (int h = 0; h < DDS_HANDS; h++){
//       fout << table -> resTable [s][h];
//     }
//   }
//   fout << endl;
// }


int main(int argc, char ** argv)
{

  int no_of_hands;

  if (argc <= 1)
  {
    printf ("Please enter no. of boards wanting to generate.\n");
    return 0;
  }
  else
  {
    try{
      no_of_hands = std::stoi (argv [1]);
    }
    catch (...)
    {
      printf ("Some exception occurred\n");
    }
  }

  ddTableDeal tableDeal;
  ddTableResults table;
  unsigned int holdings [no_of_hands][4][4];
  // srand (unsigned (time (0)));
  // srand (time (0));
  std::mt19937 g(static_cast<uint32_t>(time(0)));

  int res;
  char line[80];
  bool match;

#if defined(__linux) || defined(__APPLE__)
  SetMaxThreads(0);
#endif

  for (int handno = 0; handno < no_of_hands; handno++)
  {
    gen_hand (holdings [handno], g);
  }
  
  // for (int h = 0; h < DDS_HANDS; h++){
  //   for (int s = 0; s < DDS_SUITS; s++){
  //     printf ("line 61: %d%d: %d\n", h, s, holdings [0][h][s]);
  //   } 
  // }

  FILE* fout;
  fout = fopen ("HandRecords", "a+");

  // gen_hand (holdings [0]);
  
  for (int handno = 0; handno < no_of_hands; handno++)
  {

    for (int h = 0; h < DDS_HANDS; h++)
      for (int s = 0; s < DDS_SUITS; s++)
        tableDeal.cards[h][s] = holdings[handno][h][s];

    res = CalcDDtable(tableDeal, &table);

    if (res != RETURN_NO_FAULT)
    {
      ErrorMessage(res, line);
      printf("DDS error: %s\n", line);
    }

    // match = CompareTable(&table, handno);

    // sprintf(line,
    //         "CalcDDtable, hand %d: %s\n",
    //         handno + 1, (match ? "OK" : "ERROR"));

    PrintHand(line, tableDeal.cards);

    PrintTable(&table);

    for (int h = 0; h < DDS_HANDS; h++){
      for (int s = 0; s < DDS_SUITS; s++){
        if (h != DDS_HANDS -1 || s != DDS_SUITS -1)
          fprintf (fout, "%u,", tableDeal.cards [h][s]);
        else
          fprintf (fout, "%u", tableDeal.cards [h][s]);
      }
    }
    fprintf (fout, "|");
    for (int s = 0; s < DDS_STRAINS; s++){
      for (int h = 0; h < DDS_HANDS; h++){
        if (s != DDS_STRAINS - 1 || h != DDS_HANDS - 1)
          fprintf (fout, "%d,", table.resTable [s][h]);
        else
          fprintf (fout, "%d", table.resTable [s][h]);
      }
    }

    fprintf (fout, "\n");
  }
  fclose (fout);
}

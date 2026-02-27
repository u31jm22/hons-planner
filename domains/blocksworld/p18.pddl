<<<<<<< HEAD


(define (problem BW-rand-15)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15 )
(:init
(arm-empty)
(on b1 b15)
(on b2 b9)
(on b3 b2)
(on-table b4)
(on b5 b7)
(on b6 b10)
(on b7 b8)
(on b8 b13)
(on b9 b14)
(on b10 b5)
(on b11 b1)
(on-table b12)
(on b13 b3)
(on b14 b4)
(on b15 b12)
(clear b6)
(clear b11)
)
(:goal
(and
(on b1 b11)
(on b2 b13)
(on b3 b2)
(on b4 b14)
(on b5 b7)
(on b7 b3)
(on b8 b15)
(on b9 b8)
(on b10 b12)
(on b12 b1)
(on b15 b6))
)
)


=======
(define (problem BLOCKS-9-2)
(:domain BLOCKS)
(:objects B I C E D A G F H - block)
(:INIT (CLEAR H) (CLEAR F) (ONTABLE G) (ONTABLE F) (ON H A) (ON A D) (ON D E)
 (ON E C) (ON C I) (ON I B) (ON B G) (HANDEMPTY))
(:goal (AND (ON F G) (ON G H) (ON H D) (ON D I) (ON I E) (ON E B) (ON B C)
            (ON C A)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

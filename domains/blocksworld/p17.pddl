<<<<<<< HEAD


(define (problem BW-rand-14)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b5)
(on-table b3)
(on b4 b9)
(on-table b5)
(on b6 b4)
(on b7 b12)
(on-table b8)
(on b9 b10)
(on b10 b2)
(on b11 b7)
(on b12 b6)
(on b13 b8)
(on b14 b13)
(clear b1)
(clear b11)
(clear b14)
)
(:goal
(and
(on b1 b14)
(on b3 b8)
(on b4 b12)
(on b5 b6)
(on b6 b9)
(on b7 b5)
(on b8 b10)
(on b10 b13)
(on b11 b3)
(on b12 b2)
(on b14 b11))
)
)


=======
(define (problem BLOCKS-9-1)
(:domain BLOCKS)
(:objects H G I C D B E A F - block)
(:INIT (CLEAR F) (ONTABLE A) (ON F E) (ON E B) (ON B D) (ON D C) (ON C I)
 (ON I G) (ON G H) (ON H A) (HANDEMPTY))
(:goal (AND (ON D I) (ON I A) (ON A B) (ON B H) (ON H G) (ON G F) (ON F E)
            (ON E C)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

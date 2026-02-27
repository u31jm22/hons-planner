<<<<<<< HEAD


(define (problem BW-rand-13)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 )
(:init
(arm-empty)
(on-table b1)
(on b2 b5)
(on b3 b2)
(on b4 b11)
(on b5 b4)
(on b6 b8)
(on b7 b3)
(on b8 b13)
(on b9 b1)
(on b10 b12)
(on b11 b9)
(on-table b12)
(on-table b13)
(clear b6)
(clear b7)
(clear b10)
)
(:goal
(and
(on b2 b11)
(on b3 b13)
(on b4 b3)
(on b5 b2)
(on b9 b6)
(on b10 b5)
(on b11 b8)
(on b12 b1))
)
)


=======
(define (problem BLOCKS-9-0)
(:domain BLOCKS)
(:objects H D I A E G B F C - block)
(:INIT (CLEAR C) (CLEAR F) (ONTABLE C) (ONTABLE B) (ON F G) (ON G E) (ON E A)
 (ON A I) (ON I D) (ON D H) (ON H B) (HANDEMPTY))
(:goal (AND (ON G D) (ON D B) (ON B C) (ON C A) (ON A I) (ON I F) (ON F E)
            (ON E H)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

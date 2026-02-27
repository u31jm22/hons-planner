<<<<<<< HEAD


(define (problem BW-rand-11)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 )
(:init
(arm-empty)
(on-table b1)
(on b2 b6)
(on-table b3)
(on-table b4)
(on b5 b9)
(on b6 b4)
(on b7 b8)
(on b8 b1)
(on b9 b11)
(on b10 b5)
(on b11 b2)
(clear b3)
(clear b7)
(clear b10)
)
(:goal
(and
(on b1 b7)
(on b2 b5)
(on b3 b2)
(on b4 b9)
(on b5 b6)
(on b9 b11)
(on b10 b1)
(on b11 b3))
)
)


=======
(define (problem BLOCKS-8-1)
(:domain BLOCKS)
(:objects B A G C F D H E - block)
(:INIT (CLEAR E) (CLEAR H) (CLEAR D) (CLEAR F) (ONTABLE C) (ONTABLE G)
 (ONTABLE D) (ONTABLE F) (ON E C) (ON H A) (ON A B) (ON B G) (HANDEMPTY))
(:goal (AND (ON C D) (ON D B) (ON B G) (ON G F) (ON F H) (ON H A) (ON A E)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

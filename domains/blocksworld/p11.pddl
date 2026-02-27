<<<<<<< HEAD


(define (problem BW-rand-8)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 )
(:init
(arm-empty)
(on-table b1)
(on-table b2)
(on-table b3)
(on b4 b6)
(on b5 b4)
(on-table b6)
(on b7 b2)
(on b8 b5)
(clear b1)
(clear b3)
(clear b7)
(clear b8)
)
(:goal
(and
(on b1 b5)
(on b2 b4)
(on b5 b7)
(on b6 b1)
(on b7 b3)
(on b8 b2))
)
)


=======
(define (problem BLOCKS-7-1)
(:domain BLOCKS)
(:objects E B D F G C A - block)
(:INIT (CLEAR A) (CLEAR C) (ONTABLE G) (ONTABLE F) (ON A G) (ON C D) (ON D B)
 (ON B E) (ON E F) (HANDEMPTY))
(:goal (AND (ON A E) (ON E B) (ON B F) (ON F G) (ON G C) (ON C D)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

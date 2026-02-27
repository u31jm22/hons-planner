<<<<<<< HEAD


(define (problem BW-rand-9)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 )
(:init
(arm-empty)
(on-table b1)
(on b2 b3)
(on b3 b7)
(on b4 b5)
(on b5 b8)
(on b6 b1)
(on b7 b6)
(on-table b8)
(on b9 b4)
(clear b2)
(clear b9)
)
(:goal
(and
(on b2 b5)
(on b3 b8)
(on b5 b4)
(on b6 b1)
(on b7 b6)
(on b8 b9))
)
)


=======
(define (problem BLOCKS-7-2)
(:domain BLOCKS)
(:objects E G C D F A B - block)
(:INIT (CLEAR B) (CLEAR A) (ONTABLE F) (ONTABLE D) (ON B C) (ON C G) (ON G E)
 (ON E F) (ON A D) (HANDEMPTY))
(:goal (AND (ON E B) (ON B F) (ON F D) (ON D A) (ON A C) (ON C G)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

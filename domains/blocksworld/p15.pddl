<<<<<<< HEAD


(define (problem BW-rand-12)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 )
(:init
(arm-empty)
(on b1 b4)
(on-table b2)
(on-table b3)
(on-table b4)
(on b5 b2)
(on-table b6)
(on-table b7)
(on b8 b11)
(on b9 b7)
(on-table b10)
(on b11 b1)
(on-table b12)
(clear b3)
(clear b5)
(clear b6)
(clear b8)
(clear b9)
(clear b10)
(clear b12)
)
(:goal
(and
(on b2 b8)
(on b3 b10)
(on b4 b3)
(on b5 b4)
(on b8 b12)
(on b9 b2)
(on b10 b6)
(on b11 b1)
(on b12 b7))
)
)


=======
(define (problem BLOCKS-8-2)
(:domain BLOCKS)
(:objects F B G C H E A D - block)
(:INIT (CLEAR D) (CLEAR A) (CLEAR E) (CLEAR H) (CLEAR C) (ONTABLE G)
 (ONTABLE A) (ONTABLE E) (ONTABLE H) (ONTABLE C) (ON D B) (ON B F) (ON F G)
 (HANDEMPTY))
(:goal (AND (ON C B) (ON B E) (ON E G) (ON G F) (ON F A) (ON A D) (ON D H)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

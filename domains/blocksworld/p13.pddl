<<<<<<< HEAD


(define (problem BW-rand-10)
(:domain blocksworld-4ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 )
(:init
(arm-empty)
(on b1 b5)
(on-table b2)
(on b3 b8)
(on-table b4)
(on b5 b2)
(on b6 b1)
(on b7 b6)
(on b8 b4)
(on b9 b7)
(on b10 b3)
(clear b9)
(clear b10)
)
(:goal
(and
(on b1 b4)
(on b2 b1)
(on b3 b5)
(on b4 b9)
(on b5 b6)
(on b6 b2)
(on b7 b3)
(on b8 b7))
)
)


=======
(define (problem BLOCKS-8-0)
(:domain BLOCKS)
(:objects H G F E C B D A - block)
(:INIT (CLEAR A) (CLEAR D) (CLEAR B) (CLEAR C) (ONTABLE E) (ONTABLE F)
 (ONTABLE B) (ONTABLE C) (ON A G) (ON G E) (ON D H) (ON H F) (HANDEMPTY))
(:goal (AND (ON D F) (ON F E) (ON E H) (ON H C) (ON C A) (ON A G) (ON G B)))
)
>>>>>>> e6e1faca4ef751d715d80f51f83d279b1e3bed2f

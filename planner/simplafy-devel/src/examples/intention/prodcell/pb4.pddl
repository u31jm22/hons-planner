(define (problem pb4) (:domain prodcell)
(:objects 
    depositbelt - depbelt
    feedBelt - fedbelt
belt0 belt1 - belt
pu0 pu1 pu2 pu3 - procunit
block0 block1 block2 block3 - block
)

(:init
(connected pu0 belt1) (connected belt0 pu1) (connected feedBelt belt1) (connected pu1 belt1) (connected belt1 pu3) (connected belt1 belt1) (over block2 feedbelt) (empty belt0) (empty pu0) (connected pu3 belt0) (connected belt0 pu3) (connected belt0 belt1) (connected belt0 pu0) (connected belt1 pu2) (connected belt1 depositBelt) (over block1 feedbelt) (empty pu1) (connected pu2 belt0) (over block3 feedbelt) (connected belt0 pu2) (connected pu0 belt0) (connected belt0 depositBelt) (connected feedBelt belt0) (connected pu1 belt0) (empty belt1) (connected belt1 belt0) (connected belt1 pu0) (empty pu3) (connected pu3 belt1) (over block0 feedbelt) (connected belt1 pu1) (connected belt0 belt0) (empty pu2) (empty depositBelt) (connected pu2 belt1) )

(:desires 
(:desire (and  (finished block0)  (processed block1 pu1)  (processed block1 pu3)  (processed block0 pu2)  (finished block1)  (processed block0 pu1)  ))
(:desire (and  (finished block0)  (processed block2 pu3)  (finished block2)  (processed block0 pu2)  (processed block0 pu1)  (processed block3 pu0)  (finished block3)  (processed block1 pu1)  (processed block1 pu3)  (processed block3 pu1)  (processed block2 pu1)  (finished block1)  ))
)
)

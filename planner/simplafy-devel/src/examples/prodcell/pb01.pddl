(define (problem pb01) (:domain prodcell)
(:objects 
    depositbelt - depbelt
    feedBelt - fedbelt
    belt0 belt1 - belt
    pu0 pu1 pu2 pu3 pu4 pu5 pu6 pu7 pu8 pu9 - procunit
    block0 block1 - block
)

(:init
    (connected pu1 belt1) (empty pu4) (connected pu9 belt1) (empty depositbelt) (finished block0) (connected belt1 pu8) (connected belt0 pu8) (connected belt1 pu6) (connected pu2 belt1) (connected belt0 pu4) (connected pu3 belt1) (over block1 feedbelt) (connected belt0 depositbelt) (empty pu2) (empty pu7) (processed block0 pu5) (connected belt0 pu2) (connected belt1 pu5) (connected belt1 belt1) (connected pu8 belt1) (connected belt1 pu3) (connected pu1 belt0) (connected belt0 belt1) (connected belt0 pu7) (connected pu5 belt0) (connected pu4 belt1) (connected belt1 belt0) (connected pu6 belt0) (connected belt1 pu0) (connected pu7 belt0) (connected belt1 pu9) (empty pu8) (connected pu4 belt0) (connected feedbelt belt0) (connected pu0 belt0) (connected belt0 pu6) (connected pu5 belt1) (connected belt1 pu4) (empty belt1) (empty pu5) (empty pu3) (connected belt1 depositbelt) (processed block0 pu2) (connected belt1 pu2) (connected belt0 pu5) (connected pu9 belt0) (connected belt0 pu3) (connected pu6 belt1) (connected belt1 pu7) (connected pu2 belt0) (connected pu7 belt1) (connected pu3 belt0) (empty belt0) (connected feedbelt belt1) (empty pu0) (empty pu9) (connected pu0 belt1) (connected pu8 belt0) (connected belt0 belt0) (connected belt0 pu0) (processed block0 pu1) (connected belt0 pu9) (connected belt1 pu1) (empty pu6) (connected belt0 pu1)
)

(:goal
    (and  (finished block1)  (processed block1 pu2)  (processed block1 pu6)  (processed block1 pu8)  )
)
)

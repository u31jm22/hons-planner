(define (problem pb3) (:domain blocksworld)
(:objects 
b0 b1 b2
)

(:init
(equal b1 b1) (clear b1) (ontable b1) (equal b2 b2) (equal b0 b0) (ontable b2) (ontable b0) (clear b0) (handempty) (clear b2) )

(:desires 
(:desire (and  (clear b0)  (ontable b0)  ))
(:desire (and  (clear b0)  (clear b2)  (ontable b2)  (ontable b0)  ))
)
)

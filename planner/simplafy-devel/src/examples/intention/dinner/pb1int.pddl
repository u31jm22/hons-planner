(define (problem pb1int)
  (:domain dinner)
  (:init
    (garbage)
    (clean)
    (quiet)
  )
  (:desires
    (:desire (and
	    (dinner)
      (not (garbage))
    ))
  (:desire (and
    (present)
    ))
  )
)
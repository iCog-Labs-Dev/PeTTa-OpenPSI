(= (pushEvent $type $data) (
    if (== $data ())
        ()
        (let* (
            (($head $tail) (decons-atom $data))
            ($_ (println! (Pushing Event: $type - $head)))
            ($_ (py-call (comms.send_event ($type $head))))
        )
    (pushEvent $type $tail))
))
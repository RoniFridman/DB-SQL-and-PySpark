SELECT ChosenTrips.tripName, ChosenTrips.startDate, ChosenTrips.endDate, COUNT(*) AS pNum
FROM TravelerInTrip,
     (SELECT DISTINCT tripName,startDate,endDate
        FROM TravelerInTrip
        WHERE YEAR(startDate) = '2020' AND YEAR(endDate) = '2020'
        EXCEPT
        SELECT DISTINCT tripName,startDate,endDate
        FROM TravelerInTrip
        WHERE tID NOT IN (SELECT T1.tID
                            FROM TravelerInTrip T1 inner join TravelerInTrip T2 on T1.tID = T2.tID AND T1.tripName = T2.tripName
                            WHERE T1.endDate < T2.startDate AND DATEDIFF(month, T1.endDate, T2.startDate) >= 0
                                    AND DATEDIFF(month, T1.endDate, T2.startDate) < 3)) ChosenTrips
WHERE ChosenTrips.tripName = TravelerInTrip.tripName
AND ChosenTrips.startDate = TravelerInTrip.startDate AND ChosenTrips.endDate = TravelerInTrip.endDate
GROUP BY ChosenTrips.tripName,ChosenTrips.startDate,ChosenTrips.endDate
ORDER BY pNum DESC, tripName, startDate;

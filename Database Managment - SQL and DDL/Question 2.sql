SELECT tID1 AS tID, name, COUNT(*) AS friendsNum
FROM Friends INNER JOIN Traveler on Friends.tID1 = Traveler.tID
GROUP BY tID1, name
HAVING COUNT(tID1) >= 5
ORDER BY friendsNum DESC, tID1 DESC;
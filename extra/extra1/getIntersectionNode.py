class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def createList(nums):
    head = ListNode(nums[0])
    current = head
    for num in nums[1:]:
        current.next = ListNode(num)
        current = current.next
    return head

def getIntersectionNode(headA, headB):
    if headA is None or headB is None:
        return None

    ptrA = headA
    ptrB = headB

    while ptrA != ptrB:
        ptrA = headB if ptrA is None else ptrA.next
        ptrB = headA if ptrB is None else ptrB.next

    return ptrA

# Test case 1
intersectVal1 = 8
listA1 = createList([4,1,8,4,5])
listB1 = createList([5,6,1,8,4,5])
skipA1 = 2
skipB1 = 3

# Connect intersectVal1 node to the intersecting point in listA1
intersectNode1 = listA1
for _ in range(skipA1):
    intersectNode1 = intersectNode1.next

# Connect listB1 to the intersecting point
current = listB1
while current.next:
    current = current.next
current.next = intersectNode1

# Test case 2
intersectVal2 = 2
listA2 = createList([1,9,1,2,4])
listB2 = createList([3,2,4])
skipA2 = 3
skipB2 = 1

# Connect intersectVal2 node to the intersecting point in listB2
intersectNode2 = listB2
for _ in range(skipB2):
    intersectNode2 = intersectNode2.next

# Connect listA2 to the intersecting point
current = listA2
while current.next:
    current = current.next
current.next = intersectNode2

# Test case 3
intersectVal3 = 0
listA3 = createList([2,6,4])
listB3 = createList([1,5])
skipA3 = 3
skipB3 = 2

# No intersection in test case 3, so no need to adjust the lists
# Test case 1
intersectionNode1 = getIntersectionNode(listA1, listB1)
if intersectionNode1 is None:
    print("Test case 1: No intersection")
else:
    print(f"Test case 1: Intersected at '{intersectionNode1.val}'")

# Test case 2
intersectionNode2 = getIntersectionNode(listA2, listB2)
if intersectionNode2 is None:
    print("Test case 2: No intersection")
else:
    print(f"Test case 2: Intersected at '{intersectionNode2.val}'")

# Test case 3
intersectionNode3 = getIntersectionNode(listA3, listB3)
if intersectionNode3 is None:
    print("Test case 3: No intersection")
else:
    print(f"Test case 3: Intersected at '{intersectionNode3.val}'")

'use client';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Container, Heading, Text, Button, Flex, Card } from "@radix-ui/themes";

export default function RegisterSuccessPage() {
    const router = useRouter();
    const [showPage, setShowPage] = useState(false);

    useEffect(() => {
        const successFlag = localStorage.getItem("registerSuccess");
        if (successFlag) {
            localStorage.removeItem("registerSuccess");
            setShowPage(true);
        } else {
            router.push("/register");
        }
    }, [router]);

    if (!showPage) return null;

    return (
        <Container size="3" pt="6" pb="6">
            <Flex direction="column" align="center" justify="center" style={{ minHeight: "60vh" }}>
                <Card size="4" style={{ width: "100%", maxWidth: "400px" }}>
                    <Flex direction="column" gap="4" align="center">
                        <Heading as="h1" size="6">
                            Registered successfully!
                        </Heading>
                        <Text size="3">
                            Account Created, Yay!
                        </Text>
                        <Button
                            variant="solid"
                            highContrast
                            onClick={() => router.push("/login")}
                            style={{ width: "100%" }}
                        >
                            Go Login bro.
                        </Button>
                    </Flex>
                </Card>
            </Flex>
        </Container>
    );
}

import { Box, VStack, Image, Text, WrapItem } from "@chakra-ui/react";

interface ProductProps {
  name: string,
  price: string,
  quantity: Number,
  isInStock: boolean,
  imageUrl: string
}

export const Product = ({ name, price, quantity, isInStock, imageUrl }: ProductProps) => (
  <Box>
    <VStack>
      <Image src={imageUrl} alt={name} width='200px' />
      <Text as='b' align='left' width='200px' fontSize='sm'>{name}</Text>
      <Box>
        <Text align='left' fontSize='sm' width='200px'>{price}</Text>
        <Text align='left' fontSize='sm'>{quantity.toString()}</Text>
        {
          !isInStock ? 
          <Text align='left' fontSize='sm' color='tomato'>Out of Stock</Text> 
          : 
          null
        }
      </Box>
    </VStack>
  </Box>
);



